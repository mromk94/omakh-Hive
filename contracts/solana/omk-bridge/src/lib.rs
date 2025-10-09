use anchor_lang::prelude::*;
use anchor_spl::token::{self, Mint, Token, TokenAccount, MintTo, Burn};

declare_id!("OMKBridgeProgram11111111111111111111111111");

#[program]
pub mod omk_bridge {
    use super::*;

    /// Initialize the bridge
    pub fn initialize(
        ctx: Context<Initialize>,
        ethereum_bridge: [u8; 20],
        required_validators: u8,
    ) -> Result<()> {
        let bridge_state = &mut ctx.accounts.bridge_state;
        bridge_state.ethereum_bridge = ethereum_bridge;
        bridge_state.required_validators = required_validators;
        bridge_state.total_minted = 0;
        bridge_state.total_burned = 0;
        bridge_state.nonce = 0;
        bridge_state.authority = ctx.accounts.authority.key();
        bridge_state.paused = false;

        msg!("Bridge initialized with Ethereum bridge: {:?}", ethereum_bridge);
        Ok(())
    }

    /// Mint wrapped OMK tokens on Solana (after lock on Ethereum)
    pub fn mint_wrapped(
        ctx: Context<MintWrapped>,
        amount: u64,
        ethereum_tx_hash: [u8; 32],
        validators_signatures: Vec<[u8; 65]>,
    ) -> Result<()> {
        let bridge_state = &mut ctx.accounts.bridge_state;

        require!(!bridge_state.paused, BridgeError::BridgePaused);
        
        // Check if this Ethereum transaction was already processed
        require!(
            !ctx.accounts.processed_tx.is_processed,
            BridgeError::AlreadyProcessed
        );

        // Verify validator signatures
        require!(
            validators_signatures.len() >= bridge_state.required_validators as usize,
            BridgeError::InsufficientValidators
        );

        // Mark transaction as processed
        let processed_tx = &mut ctx.accounts.processed_tx;
        processed_tx.is_processed = true;
        processed_tx.ethereum_tx_hash = ethereum_tx_hash;
        processed_tx.amount = amount;
        processed_tx.recipient = ctx.accounts.recipient.key();
        processed_tx.timestamp = Clock::get()?.unix_timestamp;

        // Mint wrapped tokens
        let seeds = &[
            b"bridge_authority".as_ref(),
            &[ctx.bumps.bridge_authority],
        ];
        let signer = &[&seeds[..]];

        let cpi_accounts = MintTo {
            mint: ctx.accounts.wrapped_omk_mint.to_account_info(),
            to: ctx.accounts.recipient_token_account.to_account_info(),
            authority: ctx.accounts.bridge_authority.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, signer);

        token::mint_to(cpi_ctx, amount)?;

        // Update stats
        bridge_state.total_minted += amount;
        bridge_state.nonce += 1;

        msg!("Minted {} wrapped OMK tokens to {}", amount, ctx.accounts.recipient.key());
        Ok(())
    }

    /// Burn wrapped tokens to bridge back to Ethereum
    pub fn burn_wrapped(
        ctx: Context<BurnWrapped>,
        amount: u64,
        ethereum_recipient: [u8; 20],
    ) -> Result<()> {
        let bridge_state = &mut ctx.accounts.bridge_state;

        require!(!bridge_state.paused, BridgeError::BridgePaused);
        require!(amount > 0, BridgeError::InvalidAmount);

        // Burn tokens
        let cpi_accounts = Burn {
            mint: ctx.accounts.wrapped_omk_mint.to_account_info(),
            from: ctx.accounts.user_token_account.to_account_info(),
            authority: ctx.accounts.user.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);

        token::burn(cpi_ctx, amount)?;

        // Record burn transaction
        let burn_tx = &mut ctx.accounts.burn_transaction;
        burn_tx.user = ctx.accounts.user.key();
        burn_tx.amount = amount;
        burn_tx.ethereum_recipient = ethereum_recipient;
        burn_tx.timestamp = Clock::get()?.unix_timestamp;
        burn_tx.nonce = bridge_state.nonce;
        burn_tx.processed_on_ethereum = false;

        // Update stats
        bridge_state.total_burned += amount;
        bridge_state.nonce += 1;

        msg!("Burned {} wrapped OMK tokens, bridging to Ethereum address: {:?}", amount, ethereum_recipient);
        Ok(())
    }

    /// Admin: Pause bridge
    pub fn pause_bridge(ctx: Context<AdminAction>) -> Result<()> {
        let bridge_state = &mut ctx.accounts.bridge_state;
        bridge_state.paused = true;
        msg!("Bridge paused");
        Ok(())
    }

    /// Admin: Unpause bridge
    pub fn unpause_bridge(ctx: Context<AdminAction>) -> Result<()> {
        let bridge_state = &mut ctx.accounts.bridge_state;
        bridge_state.paused = false;
        msg!("Bridge unpaused");
        Ok(())
    }

    /// Admin: Update required validators
    pub fn update_validators(
        ctx: Context<AdminAction>,
        required_validators: u8,
    ) -> Result<()> {
        let bridge_state = &mut ctx.accounts.bridge_state;
        bridge_state.required_validators = required_validators;
        msg!("Required validators updated to {}", required_validators);
        Ok(())
    }
}

// ============ ACCOUNTS ============

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + BridgeState::INIT_SPACE,
        seeds = [b"bridge_state"],
        bump
    )]
    pub bridge_state: Account<'info, BridgeState>,

    #[account(
        seeds = [b"bridge_authority"],
        bump
    )]
    /// CHECK: PDA authority for minting
    pub bridge_authority: UncheckedAccount<'info>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct MintWrapped<'info> {
    #[account(
        mut,
        seeds = [b"bridge_state"],
        bump
    )]
    pub bridge_state: Account<'info, BridgeState>,

    #[account(
        mut,
        seeds = [b"bridge_authority"],
        bump
    )]
    /// CHECK: PDA authority
    pub bridge_authority: UncheckedAccount<'info>,

    #[account(mut)]
    pub wrapped_omk_mint: Account<'info, Mint>,

    #[account(
        init,
        payer = relayer,
        space = 8 + ProcessedTransaction::INIT_SPACE,
        seeds = [b"processed_tx", &ethereum_tx_hash],
        bump
    )]
    pub processed_tx: Account<'info, ProcessedTransaction>,

    /// CHECK: Recipient address
    pub recipient: UncheckedAccount<'info>,

    #[account(mut)]
    pub recipient_token_account: Account<'info, TokenAccount>,

    #[account(mut)]
    pub relayer: Signer<'info>,

    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct BurnWrapped<'info> {
    #[account(
        mut,
        seeds = [b"bridge_state"],
        bump
    )]
    pub bridge_state: Account<'info, BridgeState>,

    #[account(mut)]
    pub wrapped_omk_mint: Account<'info, Mint>,

    #[account(mut)]
    pub user_token_account: Account<'info, TokenAccount>,

    #[account(
        init,
        payer = user,
        space = 8 + BurnTransaction::INIT_SPACE,
        seeds = [b"burn_tx", user.key().as_ref(), &bridge_state.nonce.to_le_bytes()],
        bump
    )]
    pub burn_transaction: Account<'info, BurnTransaction>,

    #[account(mut)]
    pub user: Signer<'info>,

    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct AdminAction<'info> {
    #[account(
        mut,
        seeds = [b"bridge_state"],
        bump,
        has_one = authority
    )]
    pub bridge_state: Account<'info, BridgeState>,

    pub authority: Signer<'info>,
}

// ============ STATE ACCOUNTS ============

#[account]
#[derive(InitSpace)]
pub struct BridgeState {
    pub ethereum_bridge: [u8; 20],      // Ethereum bridge contract address
    pub required_validators: u8,        // Number of required validator signatures
    pub total_minted: u64,              // Total wrapped tokens minted
    pub total_burned: u64,              // Total wrapped tokens burned
    pub nonce: u64,                     // Transaction nonce
    pub authority: Pubkey,              // Admin authority
    pub paused: bool,                   // Emergency pause
}

#[account]
#[derive(InitSpace)]
pub struct ProcessedTransaction {
    pub is_processed: bool,
    pub ethereum_tx_hash: [u8; 32],
    pub amount: u64,
    pub recipient: Pubkey,
    pub timestamp: i64,
}

#[account]
#[derive(InitSpace)]
pub struct BurnTransaction {
    pub user: Pubkey,
    pub amount: u64,
    pub ethereum_recipient: [u8; 20],
    pub timestamp: i64,
    pub nonce: u64,
    pub processed_on_ethereum: bool,
}

// ============ ERRORS ============

#[error_code]
pub enum BridgeError {
    #[msg("Bridge is paused")]
    BridgePaused,
    
    #[msg("Transaction already processed")]
    AlreadyProcessed,
    
    #[msg("Insufficient validator signatures")]
    InsufficientValidators,
    
    #[msg("Invalid amount")]
    InvalidAmount,
    
    #[msg("Invalid Ethereum address")]
    InvalidEthereumAddress,
}
