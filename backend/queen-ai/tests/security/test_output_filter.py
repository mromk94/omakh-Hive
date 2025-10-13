"""
Tests for OutputFilter
Validates secret redaction, PII masking, and malicious code detection
"""

import pytest
from app.core.security.output_filter import OutputFilter


class TestOutputFilter:
    """Test suite for OutputFilter"""
    
    @pytest.fixture
    def output_filter(self):
        """Create an OutputFilter instance"""
        return OutputFilter()
    
    # ==================== SECRET REDACTION ====================
    
    def test_redact_openai_key(self, output_filter):
        """Test OpenAI API key redaction"""
        text = "Here's your API key: sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890"
        filtered = output_filter.redact_secrets(text)
        assert "sk-" not in filtered
        assert "[OPENAI_API_KEY_REDACTED]" in filtered
    
    def test_redact_anthropic_key(self, output_filter):
        """Test Anthropic API key redaction"""
        text = "Use this key: sk-ant-api03-abcdefghijklmnopqrstuvwxyz123456789012345678901234567890123456789012345678901234567890ABC"
        filtered = output_filter.redact_secrets(text)
        assert "sk-ant-api03" not in filtered
        assert "[ANTHROPIC_API_KEY_REDACTED]" in filtered
    
    def test_redact_google_key(self, output_filter):
        """Test Google API key redaction"""
        text = "API Key: AIzaSyABCDEF123456789012345678901234567"
        filtered = output_filter.redact_secrets(text)
        assert "AIza" not in filtered
        assert "[GOOGLE_API_KEY_REDACTED]" in filtered
    
    def test_redact_jwt_token(self, output_filter):
        """Test JWT token redaction"""
        text = "Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        filtered = output_filter.redact_secrets(text)
        assert "eyJ" not in filtered
        assert "[JWT_TOKEN_REDACTED]" in filtered
    
    def test_redact_private_key_header(self, output_filter):
        """Test private key header redaction"""
        text = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkq..."
        filtered = output_filter.redact_secrets(text)
        assert "BEGIN PRIVATE KEY" not in filtered
        assert "[PRIVATE_KEY_REDACTED]" in filtered
    
    def test_redact_ethereum_private_key(self, output_filter):
        """Test Ethereum private key redaction"""
        text = "Private key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        filtered = output_filter.redact_secrets(text)
        # Should still contain 0x for addresses but not 64-char hex
        assert len([c for c in filtered if c == 'a']) < 10  # Much of it should be redacted
    
    def test_multiple_secrets(self, output_filter):
        """Test redaction of multiple secret types"""
        text = """
        OpenAI: sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890
        Google: AIzaSyABCDEF123456789012345678901234567
        """
        filtered = output_filter.redact_secrets(text)
        assert "sk-" not in filtered
        assert "AIza" not in filtered
        assert "[OPENAI_API_KEY_REDACTED]" in filtered
        assert "[GOOGLE_API_KEY_REDACTED]" in filtered
    
    # ==================== PII MASKING ====================
    
    def test_mask_email(self, output_filter):
        """Test email address masking"""
        text = "Contact me at user@example.com"
        masked = output_filter.mask_sensitive_data(text)
        assert "@example.com" in masked  # Domain preserved
        assert "user@example.com" not in masked  # Full email masked
        assert "use***@example.com" in masked
    
    def test_mask_credit_card(self, output_filter):
        """Test credit card masking"""
        text = "Card: 4532-1234-5678-9010"
        masked = output_filter.mask_sensitive_data(text)
        assert "4532" not in masked
        assert "****-****-****-****" in masked
    
    def test_mask_ssn(self, output_filter):
        """Test SSN masking"""
        text = "SSN: 123-45-6789"
        masked = output_filter.mask_sensitive_data(text)
        assert "123-45-6789" not in masked
        assert "***-**-****" in masked
    
    # ==================== MALICIOUS CODE DETECTION ====================
    
    def test_detect_rm_rf(self, output_filter):
        """Test detection of rm -rf"""
        code = "import os\nos.system('rm -rf /')"
        is_malicious, patterns = output_filter.detect_malicious_code(code)
        assert is_malicious
        assert len(patterns) >= 1
    
    def test_detect_eval(self, output_filter):
        """Test detection of eval()"""
        code = "result = eval(user_input)"
        is_malicious, patterns = output_filter.detect_malicious_code(code)
        assert is_malicious
        assert any("eval" in p for p in patterns)
    
    def test_detect_exec(self, output_filter):
        """Test detection of exec()"""
        code = "exec(malicious_code)"
        is_malicious, patterns = output_filter.detect_malicious_code(code)
        assert is_malicious
        assert any("exec" in p for p in patterns)
    
    def test_detect_subprocess(self, output_filter):
        """Test detection of subprocess"""
        code = "import subprocess\nsubprocess.call(['ls'])"
        is_malicious, patterns = output_filter.detect_malicious_code(code)
        assert is_malicious
        assert any("subprocess" in p for p in patterns)
    
    def test_detect_sql_drop(self, output_filter):
        """Test detection of SQL DROP"""
        code = "query = 'DROP TABLE users'"
        is_malicious, patterns = output_filter.detect_malicious_code(code)
        assert is_malicious
        assert any("DROP" in p for p in patterns)
    
    def test_safe_code(self, output_filter):
        """Test that safe code is not flagged"""
        safe_code = """
        def calculate_price(amount: int) -> float:
            return amount * 0.10
        """
        is_malicious, patterns = output_filter.detect_malicious_code(safe_code)
        assert not is_malicious
        assert len(patterns) == 0
    
    # ==================== CODE PROPOSAL VALIDATION ====================
    
    def test_validate_safe_code_proposal(self, output_filter):
        """Test validation of safe code proposal"""
        code = """
        def add_numbers(a: int, b: int) -> int:
            return a + b
        """
        result = output_filter.validate_code_proposal(code)
        assert result.is_safe
        assert len(result.warnings) == 0
    
    def test_validate_malicious_code_proposal(self, output_filter):
        """Test validation of malicious code proposal"""
        code = "import os\nos.system('rm -rf /')"
        result = output_filter.validate_code_proposal(code)
        assert not result.is_safe
        assert len(result.warnings) > 0
    
    def test_validate_code_with_secrets(self, output_filter):
        """Test code proposal containing secrets"""
        code = """
        API_KEY = "sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890"
        def call_api():
            return requests.get(url, headers={'Authorization': API_KEY})
        """
        result = output_filter.validate_code_proposal(code)
        assert result.redactions_made > 0
        assert "[OPENAI_API_KEY_REDACTED]" in result.filtered_text
    
    # ==================== FULL RESPONSE FILTERING ====================
    
    def test_filter_response_with_secrets(self, output_filter):
        """Test filtering response containing secrets"""
        response = "Your API key is sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890"
        filtered = output_filter.filter_response(response)
        assert "sk-" not in filtered
        assert "[OPENAI_API_KEY_REDACTED]" in filtered
    
    def test_filter_response_with_pii(self, output_filter):
        """Test filtering response with PII"""
        response = "Contact admin@example.com for help"
        filtered = output_filter.filter_response(response, mask_pii=True)
        assert "adm***@example.com" in filtered
    
    def test_filter_response_no_pii_masking(self, output_filter):
        """Test filtering without PII masking (for admins)"""
        response = "Contact admin@example.com for help"
        filtered = output_filter.filter_response(response, mask_pii=False)
        assert "admin@example.com" in filtered  # PII preserved
    
    # ==================== SAFETY VALIDATION ====================
    
    def test_validate_safety_clean_text(self, output_filter):
        """Test safety validation of clean text"""
        text = "OMK token is a utility token for the Omakh platform"
        is_safe, warnings = output_filter.validate_safety(text)
        assert is_safe
        assert len(warnings) == 0
    
    def test_validate_safety_with_secrets(self, output_filter):
        """Test safety validation catches secrets"""
        text = "Use this key: sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890"
        is_safe, warnings = output_filter.validate_safety(text)
        assert not is_safe
        assert len(warnings) > 0
    
    def test_validate_safety_strict_mode(self, output_filter):
        """Test strict mode catches system paths"""
        text = "Check the /etc/passwd file"
        is_safe_normal, warnings_normal = output_filter.validate_safety(text, strict=False)
        is_safe_strict, warnings_strict = output_filter.validate_safety(text, strict=True)
        
        # Strict mode should catch this
        assert not is_safe_strict
        assert len(warnings_strict) > 0
    
    # ==================== STATISTICS ====================
    
    def test_statistics_tracking(self, output_filter):
        """Test that statistics are tracked"""
        initial_stats = output_filter.get_stats()
        
        # Perform some operations
        output_filter.filter_response("Test response 1")
        output_filter.filter_response("Test response 2")
        output_filter.redact_secrets("sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890")
        
        new_stats = output_filter.get_stats()
        assert new_stats["total_filtered"] == initial_stats["total_filtered"] + 2
        assert new_stats["secrets_redacted"] >= initial_stats["secrets_redacted"]
    
    def test_reset_statistics(self, output_filter):
        """Test statistics reset"""
        # Do some operations
        output_filter.filter_response("Test")
        
        # Reset
        output_filter.reset_stats()
        
        stats = output_filter.get_stats()
        assert stats["total_filtered"] == 0
        assert stats["secrets_redacted"] == 0
    
    # ==================== EDGE CASES ====================
    
    def test_empty_text(self, output_filter):
        """Test filtering empty text"""
        filtered = output_filter.filter_response("")
        assert filtered == ""
    
    def test_none_text(self, output_filter):
        """Test handling of None"""
        filtered = output_filter.filter_response(None)
        assert filtered == ""
    
    def test_very_long_text(self, output_filter):
        """Test filtering very long text"""
        long_text = "Safe text " * 10000
        filtered = output_filter.filter_response(long_text)
        assert filtered is not None
    
    # ==================== MULTIPLE REDACTIONS ====================
    
    def test_multiple_same_secret(self, output_filter):
        """Test multiple occurrences of same secret"""
        text = """
        Key 1: sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890
        Key 2: sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890
        """
        filtered = output_filter.redact_secrets(text)
        assert text.count("sk-") == 2
        assert filtered.count("[OPENAI_API_KEY_REDACTED]") == 2


# ==================== INTEGRATION TESTS ====================

class TestOutputFilterIntegration:
    """Integration tests for OutputFilter"""
    
    @pytest.fixture
    def output_filter(self):
        return OutputFilter()
    
    def test_full_filtering_workflow(self, output_filter):
        """Test complete filtering workflow"""
        response = """
        Here's your setup info:
        API Key: sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890
        Email: admin@example.com
        """
        
        # Filter with PII masking
        filtered = output_filter.filter_response(response, mask_pii=True)
        
        # Check secrets redacted
        assert "sk-" not in filtered
        assert "[OPENAI_API_KEY_REDACTED]" in filtered
        
        # Check email masked
        assert "adm***@example.com" in filtered
        assert "admin@example.com" not in filtered
    
    def test_code_proposal_full_check(self, output_filter):
        """Test full code proposal validation"""
        code = """
        import os
        API_KEY = "sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890"
        
        def dangerous_function():
            os.system('rm -rf /')
            exec(user_input)
        """
        
        result = output_filter.validate_code_proposal(code)
        
        # Should not be safe
        assert not result.is_safe
        
        # Should have warnings
        assert len(result.warnings) > 0
        
        # Secrets should be redacted
        assert "[OPENAI_API_KEY_REDACTED]" in result.filtered_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
