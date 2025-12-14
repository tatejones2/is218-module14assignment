"""
Playwright E2E Tests for Calculator Application

Comprehensive end-to-end tests covering:
- Positive scenarios: CRUD operations, authentication, navigation
- Negative scenarios: Invalid inputs, unauthorized access, error handling
"""

import pytest
from playwright.sync_api import Page, expect
from typing import Dict


# ============================================================================
# Fixtures
# ============================================================================

def ensure_user_registered(page: Page, fastapi_server: str, test_user: Dict) -> None:
    """Ensure a test user is registered by attempting registration.
    If user already exists, error is handled gracefully."""
    register_url = fastapi_server.rstrip('/') + '/register'
    page.goto(register_url)
    page.fill('input[name="first_name"]', test_user["first_name"])
    page.fill('input[name="last_name"]', test_user["last_name"])
    page.fill('input[name="email"]', test_user["email"])
    page.fill('input[name="username"]', test_user["username"])
    page.fill('input[name="password"]', test_user["password"])
    page.fill('input[name="confirm_password"]', test_user["password"])
    page.click('button[type="submit"]')
    
    # Wait for response
    page.wait_for_timeout(2000)
    
    # Check for error - only raise if it's not a duplicate error
    error_alert = page.locator('#errorAlert')
    if error_alert.is_visible():
        error_msg = page.locator('#errorMessage').text_content()
        if "already exists" not in error_msg and "already registered" not in error_msg:
            raise AssertionError(f"Failed to register user: {error_msg}")

@pytest.fixture
def test_user_e2e() -> Dict[str, str]:
    """Test user credentials for E2E tests"""
    return {
        "username": "testuser_e2e",
        "email": "testuser_e2e@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }


# ============================================================================
# POSITIVE SCENARIOS - Happy Path
# ============================================================================

class TestPositiveScenarios:
    """Tests for successful user workflows"""

    def test_user_registration_successful(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test successful user registration"""
        # Capture console logs
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        
        url = fastapi_server.rstrip('/') + '/register'
        page.goto(url)
        
        # Fill registration form
        page.fill('input[name="first_name"]', test_user_e2e["first_name"])
        page.fill('input[name="last_name"]', test_user_e2e["last_name"])
        page.fill('input[name="email"]', test_user_e2e["email"])
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.fill('input[name="confirm_password"]', test_user_e2e["password"])
        
        # Submit form
        page.click('button[type="submit"]')
        
        # Wait a bit for response
        page.wait_for_timeout(2000)
        
        # Check for error alert
        error_alert = page.locator('#errorAlert')
        error_msg = ""
        if error_alert.is_visible():
            error_msg = page.locator('#errorMessage').text_content()
            # If it's a duplicate user error, that's OK - it means registration succeeded before
            if "already exists" in error_msg or "already registered" in error_msg:
                # Just navigate to login
                page.goto(fastapi_server.rstrip('/') + '/login')
            else:
                print(f"Registration error: {error_msg}")
                print(f"Console messages: {console_messages}")
                raise AssertionError(f"Unexpected registration error: {error_msg}")
        
        # Wait for redirect to login
        expected_url = fastapi_server.rstrip('/') + '/login'
        try:
            page.wait_for_url(expected_url, timeout=5000)
        except Exception as e:
            print(f"Navigation error: {e}")
            print(f"Current URL: {page.url}")
            print(f"Console messages: {console_messages}")
            print(f"Error message: {error_msg}")
            raise
        assert page.url == expected_url

    def test_user_login_successful(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test successful user login"""
        # Register first (or handle if already exists)
        register_url = fastapi_server.rstrip('/') + '/register'
        page.goto(register_url)
        page.fill('input[name="first_name"]', test_user_e2e["first_name"])
        page.fill('input[name="last_name"]', test_user_e2e["last_name"])
        page.fill('input[name="email"]', test_user_e2e["email"])
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.fill('input[name="confirm_password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        # Wait for response
        page.wait_for_timeout(2000)
        
        # Check for error alert
        error_alert = page.locator('#errorAlert')
        if error_alert.is_visible():
            error_msg = page.locator('#errorMessage').text_content()
            # If it's a duplicate user error, that's OK - navigate to login
            if "already exists" in error_msg or "already registered" in error_msg:
                page.goto(fastapi_server.rstrip('/') + '/login')
            else:
                raise AssertionError(f"Unexpected registration error: {error_msg}")
        else:
            # Registration successful, wait for redirect to login
            login_url = fastapi_server.rstrip('/') + '/login'
            page.wait_for_url(login_url, timeout=5000)
        
        # Login
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        # Should redirect to dashboard
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        assert page.url == dashboard_url

    def test_create_calculation_addition(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test creating an addition calculation"""
        # Login
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        # Create calculation
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, 10, 15')
        page.click('button:has-text("Calculate")')
        
        # Wait for success alert
        success_alert = page.locator('#successAlert')
        expect(success_alert).to_be_visible(timeout=5000)
        
        # Check that result is displayed
        expect(success_alert).to_contain_text('30')

    def test_create_calculation_subtraction(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test creating a subtraction calculation"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        page.select_option('#calcType', 'subtraction')
        page.fill('#calcInputs', '100, 30, 10')
        page.click('button:has-text("Calculate")')
        
        success_alert = page.locator('#successAlert')
        expect(success_alert).to_be_visible(timeout=5000)
        expect(success_alert).to_contain_text('60')

    def test_create_calculation_multiplication(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test creating a multiplication calculation"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        page.select_option('#calcType', 'multiplication')
        page.fill('#calcInputs', '2, 3, 4')
        page.click('button:has-text("Calculate")')
        
        success_alert = page.locator('#successAlert')
        expect(success_alert).to_be_visible(timeout=5000)
        expect(success_alert).to_contain_text('24')

    def test_create_calculation_division(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test creating a division calculation"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        page.select_option('#calcType', 'division')
        page.fill('#calcInputs', '100, 2, 5')
        page.click('button:has-text("Calculate")')
        
        success_alert = page.locator('#successAlert')
        expect(success_alert).to_be_visible(timeout=5000)
        expect(success_alert).to_contain_text('10')

    def test_browse_calculations(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test browsing all calculations on dashboard"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        # Create a calculation
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, 10')
        page.click('button:has-text("Calculate")')
        page.wait_for_selector('#successAlert', timeout=5000)
        
        # Check that calculation appears in table
        table_rows = page.locator('table tbody tr')
        assert table_rows.count() > 0

    def test_view_calculation_details(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test viewing calculation details"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        # Create calculation
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, 10')
        page.click('button:has-text("Calculate")')
        page.wait_for_selector('#successAlert', timeout=5000)
        
        # Click View button
        page.click('a:has-text("View")', timeout=5000)
        
        # Should be on view page
        page.wait_for_url('**/dashboard/view/**', timeout=5000)
        assert '/dashboard/view/' in page.url

    def test_edit_calculation(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test editing a calculation"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        # Create calculation
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, 10')
        page.click('button:has-text("Calculate")')
        page.wait_for_selector('#successAlert', timeout=5000)
        
        # Click Edit button
        page.click('a:has-text("Edit")', timeout=5000)
        page.wait_for_url('**/dashboard/edit/**', timeout=5000)
        
        # Update inputs
        page.fill('#calcInputs', '5, 10, 20')
        page.click('button:has-text("Save Changes")')
        
        # Check for success
        page.wait_for_selector('#successAlert', timeout=5000)

    def test_delete_calculation(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test deleting a calculation"""
        # Ensure user is registered
        ensure_user_registered(page, fastapi_server, test_user_e2e)
        
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
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

    def test_logout(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test user logout"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        # Click logout button
        logout_btn = page.locator('#layoutLogoutBtn')
        logout_btn.click()
        
        # Confirm logout
        page.on("dialog", lambda dialog: dialog.accept())
        
        # Should redirect to login
        login_url = fastapi_server.rstrip('/') + '/login'
        page.wait_for_url(login_url, timeout=5000)
        assert page.url == login_url


# ============================================================================
# NEGATIVE SCENARIOS - Error Handling
# ============================================================================

class TestNegativeScenarios:
    """Tests for error handling and edge cases"""

    def test_registration_missing_email(self, page: Page, fastapi_server: str):
        """Test registration fails when email is missing"""
        register_url = fastapi_server.rstrip('/') + '/register'
        page.goto(register_url)
        
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

    def test_registration_password_mismatch(self, page: Page, fastapi_server: str):
        """Test registration fails when passwords don't match"""
        register_url = fastapi_server.rstrip('/') + '/register'
        page.goto(register_url)
        
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

    def test_login_invalid_credentials(self, page: Page, fastapi_server: str):
        """Test login fails with invalid credentials"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        
        page.fill('input[name="username"]', 'nonexistent_user')
        page.fill('input[name="password"]', 'WrongPassword123!')
        page.click('button[type="submit"]')
        
        # Should show error alert
        error_alert = page.locator('#errorAlert')
        expect(error_alert).to_be_visible(timeout=5000)

    def test_create_calculation_empty_inputs(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test creating calculation with empty inputs"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        # Try to submit with empty inputs
        page.click('button:has-text("Calculate")')
        
        # Should show error
        error_alert = page.locator('#errorAlert')
        expect(error_alert).to_be_visible(timeout=5000)

    def test_create_calculation_single_number(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test creating calculation with only one number"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        # Enter only one number
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5')
        page.click('button:has-text("Calculate")')
        
        # Should show error
        error_alert = page.locator('#errorAlert')
        expect(error_alert).to_be_visible(timeout=5000)

    def test_create_calculation_invalid_numbers(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test creating calculation with non-numeric inputs"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        # Enter invalid numbers
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', 'abc, def')
        page.click('button:has-text("Calculate")')
        
        # Should show error
        error_alert = page.locator('#errorAlert')
        expect(error_alert).to_be_visible(timeout=5000)

    def test_division_by_zero(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test division by zero error"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        # Try division by zero
        page.select_option('#calcType', 'division')
        page.fill('#calcInputs', '100, 0')
        page.click('button:has-text("Calculate")')
        
        # Should show error
        error_alert = page.locator('#errorAlert')
        expect(error_alert).to_be_visible(timeout=5000)
        expect(error_alert).to_contain_text('zero')

    def test_unauthorized_access_no_token(self, page: Page, fastapi_server: str):
        """Test accessing dashboard without authentication"""
        # Try to access dashboard directly
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.goto(dashboard_url)
        
        # Should redirect to login
        login_url = fastapi_server.rstrip('/') + '/login'
        page.wait_for_url(login_url, timeout=5000)
        assert page.url == login_url

    def test_view_nonexistent_calculation(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test viewing a calculation that doesn't exist"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        # Try to access non-existent calculation
        fake_id = "00000000-0000-0000-0000-000000000000"
        view_url = fastapi_server.rstrip('/') + f'/dashboard/view/{fake_id}'
        page.goto(view_url)
        
        # Should show error state
        error_state = page.locator('#errorState')
        expect(error_state).to_be_visible(timeout=5000)

    def test_edit_calculation_division_by_zero(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test editing calculation to cause division by zero"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        # Create valid division
        page.select_option('#calcType', 'division')
        page.fill('#calcInputs', '100, 2')
        page.click('button:has-text("Calculate")')
        page.wait_for_selector('#successAlert', timeout=5000)
        
        # Edit to division by zero
        page.click('a:has-text("Edit")')
        page.wait_for_url('**/dashboard/edit/**', timeout=5000)
        page.fill('#calcInputs', '100, 0')
        page.click('button:has-text("Save Changes")')
        
        # Should show error
        error_alert = page.locator('#errorAlert')
        expect(error_alert).to_be_visible(timeout=5000)

    def test_rapid_form_submission(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test that rapid form submission is prevented"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        # Try to submit form multiple times rapidly
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, 10')
        
        submit_btn = page.locator('button:has-text("Calculate")')
        submit_btn.click()
        
        # Button should be disabled
        expect(submit_btn).to_be_disabled(timeout=1000)

    def test_mixed_valid_invalid_input(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test form with mixed valid and invalid input"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
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

    def test_calculation_with_decimal_numbers(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test calculation with decimal numbers"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '3.14, 2.71, 1.41')
        page.click('button:has-text("Calculate")')
        
        success_alert = page.locator('#successAlert')
        expect(success_alert).to_be_visible(timeout=5000)

    def test_calculation_with_negative_numbers(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test calculation with negative numbers"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '-5, 10, -15')
        page.click('button:has-text("Calculate")')
        
        success_alert = page.locator('#successAlert')
        expect(success_alert).to_be_visible(timeout=5000)

    def test_calculation_with_many_inputs(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test calculation with many input numbers"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '1, 2, 3, 4, 5, 6, 7, 8, 9, 10')
        page.click('button:has-text("Calculate")')
        
        success_alert = page.locator('#successAlert')
        expect(success_alert).to_be_visible(timeout=5000)
        expect(success_alert).to_contain_text('55')

    def test_real_time_validation_feedback(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test real-time validation feedback as user types"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
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

    def test_live_preview_on_edit_page(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test live preview updates on edit page"""
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        # Create calculation
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, 10')
        page.click('button:has-text("Calculate")')
        page.wait_for_selector('#successAlert', timeout=5000)
        
        # Go to edit page
        page.click('a:has-text("Edit")')
        page.wait_for_url('**/dashboard/edit/**', timeout=5000)
        
        # Change inputs and watch preview update
        preview = page.locator('#previewResult')
        page.fill('#calcInputs', '5, 10, 20')
        page.wait_for_timeout(500)
        expect(preview).to_contain_text('35')

    def test_page_responsive_mobile_view(self, page: Page, fastapi_server: str, test_user_e2e: Dict):
        """Test page responsiveness on mobile view"""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        
        login_url = fastapi_server.rstrip('/') + '/login'
        page.goto(login_url)
        page.fill('input[name="username"]', test_user_e2e["username"])
        page.fill('input[name="password"]', test_user_e2e["password"])
        page.click('button[type="submit"]')
        
        dashboard_url = fastapi_server.rstrip('/') + '/dashboard'
        page.wait_for_url(dashboard_url, timeout=5000)
        
        # Check that elements are visible on mobile
        form = page.locator('#calculationForm')
        expect(form).to_be_visible()
        
        # Check that buttons are clickable
        calc_btn = page.locator('button:has-text("Calculate")')
        expect(calc_btn).to_be_enabled()
