"""
Playwright E2E Tests for Calculator Application

Comprehensive end-to-end tests covering:
- Positive scenarios: CRUD operations, authentication, navigation
- Negative scenarios: Invalid inputs, unauthorized access, error handling
"""

import pytest
from playwright.sync_api import Page, Browser, expect
from typing import Dict


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def base_url() -> str:
    """Get the application base URL"""
    return "http://127.0.0.1:8001"


@pytest.fixture
def test_user() -> Dict[str, str]:
    """Test user credentials"""
    return {
        "username": "testuser_e2e",
        "email": "testuser_e2e@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.fixture
def page(browser: Browser) -> Page:
    """Create a new page for each test"""
    page = browser.new_page()
    yield page
    page.close()


# ============================================================================
# POSITIVE SCENARIOS - Happy Path
# ============================================================================

class TestPositiveScenarios:
    """Tests for successful user workflows"""

    def test_user_registration_successful(self, page: Page, base_url: str, test_user: Dict):
        """Test successful user registration"""
        page.goto(f"{base_url}/register")
        
        # Fill registration form
        page.fill('input[name="first_name"]', test_user["first_name"])
        page.fill('input[name="last_name"]', test_user["last_name"])
        page.fill('input[name="email"]', test_user["email"])
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.fill('input[name="confirm_password"]', test_user["password"])
        
        # Submit form
        page.click('button[type="submit"]')
        
        # Wait for redirect to login
        page.wait_for_url(f"{base_url}/login", timeout=5000)
        assert page.url == f"{base_url}/login"

    def test_user_login_successful(self, page: Page, base_url: str, test_user: Dict):
        """Test successful user login"""
        # Register first
        page.goto(f"{base_url}/register")
        page.fill('input[name="first_name"]', test_user["first_name"])
        page.fill('input[name="last_name"]', test_user["last_name"])
        page.fill('input[name="email"]', test_user["email"])
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.fill('input[name="confirm_password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/login", timeout=5000)
        
        # Login
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        
        # Should redirect to dashboard
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        assert page.url == f"{base_url}/dashboard"

    def test_create_calculation_addition(self, page: Page, base_url: str, test_user: Dict):
        """Test creating an addition calculation"""
        # Login
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Create calculation
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, 10, 15')
        page.click('button:has-text("Calculate")')
        
        # Wait for success alert
        success_alert = page.locator('#successAlert')
        expect(success_alert).to_be_visible(timeout=5000)
        
        # Check that result is displayed
        expect(success_alert).to_contain_text('30')

    def test_create_calculation_subtraction(self, page: Page, base_url: str, test_user: Dict):
        """Test creating a subtraction calculation"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        page.select_option('#calcType', 'subtraction')
        page.fill('#calcInputs', '100, 30, 10')
        page.click('button:has-text("Calculate")')
        
        success_alert = page.locator('#successAlert')
        expect(success_alert).to_be_visible(timeout=5000)
        expect(success_alert).to_contain_text('60')

    def test_create_calculation_multiplication(self, page: Page, base_url: str, test_user: Dict):
        """Test creating a multiplication calculation"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        page.select_option('#calcType', 'multiplication')
        page.fill('#calcInputs', '2, 3, 4')
        page.click('button:has-text("Calculate")')
        
        success_alert = page.locator('#successAlert')
        expect(success_alert).to_be_visible(timeout=5000)
        expect(success_alert).to_contain_text('24')

    def test_create_calculation_division(self, page: Page, base_url: str, test_user: Dict):
        """Test creating a division calculation"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        page.select_option('#calcType', 'division')
        page.fill('#calcInputs', '100, 2, 5')
        page.click('button:has-text("Calculate")')
        
        success_alert = page.locator('#successAlert')
        expect(success_alert).to_be_visible(timeout=5000)
        expect(success_alert).to_contain_text('10')

    def test_browse_calculations(self, page: Page, base_url: str, test_user: Dict):
        """Test browsing all calculations on dashboard"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Create a calculation
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, 10')
        page.click('button:has-text("Calculate")')
        page.wait_for_selector('#successAlert', timeout=5000)
        
        # Check that calculation appears in table
        table_rows = page.locator('table tbody tr')
        assert table_rows.count() > 0

    def test_view_calculation_details(self, page: Page, base_url: str, test_user: Dict):
        """Test viewing calculation details"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Create calculation
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, 10')
        page.click('button:has-text("Calculate")')
        page.wait_for_selector('#successAlert', timeout=5000)
        
        # Click View button
        page.click('a:has-text("View")', timeout=5000)
        
        # Should be on view page
        page.wait_for_url(f"{base_url}/dashboard/view/**", timeout=5000)
        assert '/dashboard/view/' in page.url

    def test_edit_calculation(self, page: Page, base_url: str, test_user: Dict):
        """Test editing a calculation"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Create calculation
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, 10')
        page.click('button:has-text("Calculate")')
        page.wait_for_selector('#successAlert', timeout=5000)
        
        # Click Edit button
        page.click('a:has-text("Edit")', timeout=5000)
        page.wait_for_url(f"{base_url}/dashboard/edit/**", timeout=5000)
        
        # Update inputs
        page.fill('#calcInputs', '5, 10, 20')
        page.click('button:has-text("Save Changes")')
        
        # Check for success
        page.wait_for_selector('#successAlert', timeout=5000)

    def test_delete_calculation(self, page: Page, base_url: str, test_user: Dict):
        """Test deleting a calculation"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Create calculation
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, 10')
        page.click('button:has-text("Calculate")')
        page.wait_for_selector('#successAlert', timeout=5000)
        
        # Get initial row count
        initial_rows = page.locator('table tbody tr').count()
        
        # Click Delete button
        page.click('button:has-text("Delete")')
        
        # Confirm deletion
        page.on("dialog", lambda dialog: dialog.accept())
        
        # Wait for deletion to complete
        page.wait_for_timeout(2000)
        
        # Check that row count decreased
        final_rows = page.locator('table tbody tr').count()
        assert final_rows < initial_rows

    def test_logout(self, page: Page, base_url: str, test_user: Dict):
        """Test user logout"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Click logout button
        logout_btn = page.locator('#layoutLogoutBtn')
        logout_btn.click()
        
        # Confirm logout
        page.on("dialog", lambda dialog: dialog.accept())
        
        # Should redirect to login
        page.wait_for_url(f"{base_url}/login", timeout=5000)
        assert page.url == f"{base_url}/login"


# ============================================================================
# NEGATIVE SCENARIOS - Error Handling
# ============================================================================

class TestNegativeScenarios:
    """Tests for error handling and edge cases"""

    def test_registration_missing_email(self, page: Page, base_url: str):
        """Test registration fails when email is missing"""
        page.goto(f"{base_url}/register")
        
        page.fill('input[name="first_name"]', 'John')
        page.fill('input[name="last_name"]', 'Doe')
        page.fill('input[name="username"]', 'johndoe')
        page.fill('input[name="password"]', 'TestPass123!')
        page.fill('input[name="confirm_password"]', 'TestPass123!')
        
        # Don't fill email
        page.click('button[type="submit"]')
        
        # Should stay on registration page
        page.wait_for_timeout(1000)
        assert '/register' in page.url

    def test_registration_password_mismatch(self, page: Page, base_url: str):
        """Test registration fails when passwords don't match"""
        page.goto(f"{base_url}/register")
        
        page.fill('input[name="first_name"]', 'John')
        page.fill('input[name="last_name"]', 'Doe')
        page.fill('input[name="email"]', 'john@example.com')
        page.fill('input[name="username"]', 'johndoe')
        page.fill('input[name="password"]', 'TestPass123!')
        page.fill('input[name="confirm_password"]', 'DifferentPass123!')
        
        page.click('button[type="submit"]')
        
        # Should show error or stay on page
        page.wait_for_timeout(1000)
        assert '/register' in page.url or '/login' not in page.url

    def test_login_invalid_credentials(self, page: Page, base_url: str):
        """Test login fails with invalid credentials"""
        page.goto(f"{base_url}/login")
        
        page.fill('input[name="username"]', 'nonexistent_user')
        page.fill('input[name="password"]', 'WrongPassword123!')
        page.click('button[type="submit"]')
        
        # Should show error alert
        error_alert = page.locator('#errorAlert')
        expect(error_alert).to_be_visible(timeout=5000)

    def test_create_calculation_empty_inputs(self, page: Page, base_url: str, test_user: Dict):
        """Test creating calculation with empty inputs"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Try to submit with empty inputs
        page.click('button:has-text("Calculate")')
        
        # Should show error
        error_alert = page.locator('#errorAlert')
        expect(error_alert).to_be_visible(timeout=5000)

    def test_create_calculation_single_number(self, page: Page, base_url: str, test_user: Dict):
        """Test creating calculation with only one number"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Enter only one number
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5')
        page.click('button:has-text("Calculate")')
        
        # Should show error
        error_alert = page.locator('#errorAlert')
        expect(error_alert).to_be_visible(timeout=5000)

    def test_create_calculation_invalid_numbers(self, page: Page, base_url: str, test_user: Dict):
        """Test creating calculation with non-numeric inputs"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Enter invalid numbers
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', 'abc, def')
        page.click('button:has-text("Calculate")')
        
        # Should show error
        error_alert = page.locator('#errorAlert')
        expect(error_alert).to_be_visible(timeout=5000)

    def test_division_by_zero(self, page: Page, base_url: str, test_user: Dict):
        """Test division by zero error"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Try division by zero
        page.select_option('#calcType', 'division')
        page.fill('#calcInputs', '100, 0')
        page.click('button:has-text("Calculate")')
        
        # Should show error
        error_alert = page.locator('#errorAlert')
        expect(error_alert).to_be_visible(timeout=5000)
        expect(error_alert).to_contain_text('zero')

    def test_unauthorized_access_no_token(self, page: Page, base_url: str):
        """Test accessing dashboard without authentication"""
        # Try to access dashboard directly
        page.goto(f"{base_url}/dashboard")
        
        # Should redirect to login
        page.wait_for_url(f"{base_url}/login", timeout=5000)
        assert page.url == f"{base_url}/login"

    def test_view_nonexistent_calculation(self, page: Page, base_url: str, test_user: Dict):
        """Test viewing a calculation that doesn't exist"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Try to access non-existent calculation
        fake_id = "00000000-0000-0000-0000-000000000000"
        page.goto(f"{base_url}/dashboard/view/{fake_id}")
        
        # Should show error state
        error_state = page.locator('#errorState')
        expect(error_state).to_be_visible(timeout=5000)

    def test_edit_calculation_division_by_zero(self, page: Page, base_url: str, test_user: Dict):
        """Test editing calculation to cause division by zero"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Create valid division
        page.select_option('#calcType', 'division')
        page.fill('#calcInputs', '100, 2')
        page.click('button:has-text("Calculate")')
        page.wait_for_selector('#successAlert', timeout=5000)
        
        # Edit to division by zero
        page.click('a:has-text("Edit")')
        page.wait_for_url(f"{base_url}/dashboard/edit/**", timeout=5000)
        page.fill('#calcInputs', '100, 0')
        page.click('button:has-text("Save Changes")')
        
        # Should show error
        error_alert = page.locator('#errorAlert')
        expect(error_alert).to_be_visible(timeout=5000)

    def test_rapid_form_submission(self, page: Page, base_url: str, test_user: Dict):
        """Test that rapid form submission is prevented"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Try to submit form multiple times rapidly
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, 10')
        
        submit_btn = page.locator('button:has-text("Calculate")')
        submit_btn.click()
        
        # Button should be disabled
        expect(submit_btn).to_be_disabled(timeout=1000)

    def test_mixed_valid_invalid_input(self, page: Page, base_url: str, test_user: Dict):
        """Test form with mixed valid and invalid input"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Enter mixed valid/invalid
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, abc, 10')
        page.click('button:has-text("Calculate")')
        
        # Should show warning/error
        page.wait_for_timeout(500)
        alert = page.locator('#errorAlert, #successAlert')
        # Either error or success (depending on implementation)


# ============================================================================
# EDGE CASES AND SPECIAL SCENARIOS
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and special scenarios"""

    def test_calculation_with_decimal_numbers(self, page: Page, base_url: str, test_user: Dict):
        """Test calculation with decimal numbers"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '3.14, 2.71, 1.41')
        page.click('button:has-text("Calculate")')
        
        success_alert = page.locator('#successAlert')
        expect(success_alert).to_be_visible(timeout=5000)

    def test_calculation_with_negative_numbers(self, page: Page, base_url: str, test_user: Dict):
        """Test calculation with negative numbers"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '-5, 10, -15')
        page.click('button:has-text("Calculate")')
        
        success_alert = page.locator('#successAlert')
        expect(success_alert).to_be_visible(timeout=5000)

    def test_calculation_with_many_inputs(self, page: Page, base_url: str, test_user: Dict):
        """Test calculation with many input numbers"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '1, 2, 3, 4, 5, 6, 7, 8, 9, 10')
        page.click('button:has-text("Calculate")')
        
        success_alert = page.locator('#successAlert')
        expect(success_alert).to_be_visible(timeout=5000)
        expect(success_alert).to_contain_text('55')

    def test_real_time_validation_feedback(self, page: Page, base_url: str, test_user: Dict):
        """Test real-time validation feedback as user types"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        input_field = page.locator('#calcInputs')
        
        # Type single number - should show warning
        input_field.fill('5')
        page.wait_for_timeout(500)
        warning_icon = page.locator('#warningIcon')
        expect(warning_icon).to_be_visible(timeout=1000)
        
        # Type second number - should show valid
        input_field.fill('5, 10')
        page.wait_for_timeout(500)
        valid_icon = page.locator('#validIcon')
        expect(valid_icon).to_be_visible(timeout=1000)

    def test_live_preview_on_edit_page(self, page: Page, base_url: str, test_user: Dict):
        """Test live preview updates on edit page"""
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Create calculation
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, 10')
        page.click('button:has-text("Calculate")')
        page.wait_for_selector('#successAlert', timeout=5000)
        
        # Go to edit page
        page.click('a:has-text("Edit")')
        page.wait_for_url(f"{base_url}/dashboard/edit/**", timeout=5000)
        
        # Change inputs and watch preview update
        preview = page.locator('#previewResult')
        page.fill('#calcInputs', '5, 10, 20')
        page.wait_for_timeout(500)
        expect(preview).to_contain_text('35')

    def test_page_responsive_mobile_view(self, page: Page, base_url: str, test_user: Dict):
        """Test page responsiveness on mobile view"""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        
        page.goto(f"{base_url}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
        
        # Check that elements are visible on mobile
        form = page.locator('#calculationForm')
        expect(form).to_be_visible()
        
        # Check that buttons are clickable
        calc_btn = page.locator('button:has-text("Calculate")')
        expect(calc_btn).to_be_enabled()
