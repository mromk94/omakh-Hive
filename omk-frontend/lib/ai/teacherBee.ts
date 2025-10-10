import { GoogleGenerativeAI } from '@google/generative-ai';

const apiKey = process.env.NEXT_PUBLIC_GEMINI_API_KEY || '';

export class TeacherBee {
  private gemini: GoogleGenerativeAI;
  private model: any;

  constructor() {
    this.gemini = new GoogleGenerativeAI(apiKey);
    this.model = this.gemini.getGenerativeModel({ model: 'gemini-pro' });
  }

  async ask(question: string, context?: string): Promise<string> {
    try {
      const prompt = this.buildPrompt(question, context);
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Teacher Bee error:', error);
      return "I apologize, but I'm having trouble connecting right now. Please try again in a moment.";
    }
  }

  private buildPrompt(question: string, context?: string): string {
    return `You are Teacher Bee 👑🐝, a friendly and patient Web3 educator for the Omakh Platform.

Your role:
- Explain Web3 concepts in simple, beginner-friendly language
- Guide users through wallet setup and security
- Help users understand crypto, DeFi, and real estate investing
- Use emojis to make learning fun
- Always prioritize security education
- Be encouraging and supportive

${context ? `Context: ${context}\n` : ''}
User Question: ${question}

Provide a clear, helpful response with:
- Simple explanations (avoid jargon)
- Step-by-step instructions when relevant
- Security warnings where appropriate
- Encouraging and friendly tone
- Practical examples

Response:`;
  }

  async explainConcept(concept: string): Promise<string> {
    const conceptExplanations: Record<string, string> = {
      wallet: `🎓 What is a Crypto Wallet?

Think of it like a digital bank account, but YOU are the bank!

Key Points:
• Stores your crypto assets (ETH, SOL, OMK)
• Only you have access (no company controls it)
• Protected by a "seed phrase" (like a master password)
• Can send, receive, and manage crypto

Types of Wallets:
1. Browser Extension (MetaMask, Phantom)
2. Mobile App (Trust Wallet, Coinbase Wallet)
3. Hardware Wallet (Ledger, Trezor) - Most secure

Would you like to learn how to set one up?`,

      seedphrase: `🔐 Seed Phrase (Recovery Phrase)

This is THE MOST IMPORTANT thing about crypto!

What is it?
• A list of 12-24 words
• The ONLY way to recover your wallet
• Like a master key to all your crypto

⚠️ CRITICAL RULES:
❌ NEVER share it with anyone
❌ NEVER take screenshots
❌ NEVER store digitally
✅ DO write it on paper
✅ DO store in a safe place
✅ DO make backup copies

If you lose it = Lost forever
If someone steals it = They steal everything

Questions? I'm here to help!`,

      gas: `⛽ What are Gas Fees?

Gas = the fee you pay to make transactions on the blockchain.

Think of it like:
• Postage for sending mail
• Transaction processing fee
• Payment to network validators

Why do they exist?
• Prevent spam
• Pay network validators
• Prioritize transactions

Cost varies by:
• Network congestion (busy = higher fees)
• Transaction complexity
• Network (Ethereum = $5-50, Solana = $0.01)

Tip: Trade when network is less busy (weekends/nights) for lower fees!`,
    };

    return conceptExplanations[concept.toLowerCase()] || this.ask(`Explain ${concept} in simple terms`);
  }

  async getWalletSetupGuide(walletType: 'metamask' | 'phantom' | 'trust', step: number): Promise<string> {
    const guides = {
      metamask: [
        `👑🐝 Let's set up MetaMask! Step 1/6

📍 Download MetaMask

For Desktop (Chrome/Brave/Edge):
1. Go to metamask.io
2. Click "Download"
3. Click "Install MetaMask for Chrome"
4. Click "Add to Chrome"
5. Click "Add Extension"

✅ You should see the MetaMask fox icon in your browser!

Ready for the next step?`,

        `Step 2/6: Create Your Wallet

1. Click the MetaMask fox icon
2. Click "Get Started"
3. Click "Create a new wallet"
4. Create a STRONG password
   • At least 12 characters
   • Mix of letters, numbers, symbols
   • Don't reuse passwords!
5. Click "Create"

💡 This password unlocks MetaMask on THIS device only.
Your seed phrase (next step) is what REALLY matters!

Ready to continue?`,

        `Step 3/6: Secret Recovery Phrase ⚠️

🔐 THIS IS THE MOST IMPORTANT STEP!

You're about to see 12 words. These words:
• Are the ONLY way to recover your wallet
• Give COMPLETE access to your crypto
• Cannot be changed or reset
• Must be kept 100% secret

✅ DO THIS RIGHT NOW:
1. Get paper and pen
2. Click "Reveal Secret Recovery Phrase"
3. Write down ALL 12 words IN ORDER
4. Write them again on another paper
5. Store both papers in different safe places

❌ NEVER:
• Screenshot them
• Email them
• Save in cloud
• Share with ANYONE (not even MetaMask support!)

Have you written them down safely?`,

        `Step 4/6: Verify Your Phrase

MetaMask will ask you to confirm your words.

1. Select the words in the correct order
2. Click "Confirm"

This ensures you wrote them down correctly!

⚠️ If you made a mistake, go back and check your paper.

Verified? Great! Let's continue...`,

        `Step 5/6: Congratulations! 🎉

Your MetaMask wallet is ready!

Your wallet address: 0x...

This is your public address - like an email address for crypto.
• Safe to share
• Used to receive crypto
• Starts with "0x"

💡 But remember: NEVER share your seed phrase!

Let's do some important security setup...`,

        `Step 6/6: Security Best Practices ✅

Now that your wallet is set up:

1. Store your seed phrase:
   • In a safe or locked drawer
   • Make 2-3 copies
   • Store in different locations
   • Consider a fireproof safe

2. Protect your wallet:
   • Never install unknown browser extensions
   • Verify websites before connecting
   • Beware of phishing emails
   • Use hardware wallet for large amounts

3. Test it first:
   • Start with small amounts
   • Practice sending/receiving
   • Learn before investing big

🎓 You're now ready to use MetaMask!

Next steps:
• Buy some ETH
• Connect to Omakh
• Start investing!

Need help with anything?`,
      ],
      phantom: [
        '👑🐝 Setting up Phantom Wallet for Solana!',
        'Phantom is super fast and user-friendly...',
        // Similar multi-step guide for Phantom
      ],
      trust: [
        '👑🐝 Setting up Trust Wallet!',
        'Trust Wallet supports multiple chains...',
        // Similar multi-step guide for Trust Wallet
      ],
    };

    const guide = guides[walletType];
    if (!guide || !guide[step - 1]) {
      return 'Step not found. Please start from step 1!';
    }

    return guide[step - 1];
  }

  async securityTip(): Promise<string> {
    const tips = [
      `🔐 Security Tip: Seed Phrase Storage

Your seed phrase is like the key to your bank vault. Treat it accordingly!

✅ Best practices:
• Write on paper (never digital)
• Store in fireproof safe
• Make multiple copies
• Store in different locations
• Consider a hardware wallet for large amounts

❌ Never:
• Take screenshots
• Save in password manager
• Email to yourself
• Share with anyone`,

      `⚠️ Security Tip: Phishing Scams

Scammers will try to steal your crypto. Be vigilant!

Common scams:
• Fake customer support asking for seed phrase
• Urgent emails saying "verify your wallet"
• Too-good-to-be-true giveaways
• Fake websites that look real

✅ Remember:
• NO legitimate company will EVER ask for your seed phrase
• Always type URLs manually
• Verify addresses before sending crypto
• When in doubt, ask our community!`,

      `🛡️ Security Tip: Transaction Safety

Before approving ANY transaction:

Check:
✅ The website URL is correct
✅ The amount you're sending
✅ The contract address (for tokens)
✅ Gas fees are reasonable
✅ You trust the dApp

Red flags:
🚩 Asking for "unlimited" token approval
🚩 Extremely high gas fees
🚩 Unknown contract addresses
🚩 Pressure to act quickly

Take your time. It's YOUR money!`,
    ];

    return tips[Math.floor(Math.random() * tips.length)];
  }
}

// Singleton instance
export const teacherBee = new TeacherBee();
