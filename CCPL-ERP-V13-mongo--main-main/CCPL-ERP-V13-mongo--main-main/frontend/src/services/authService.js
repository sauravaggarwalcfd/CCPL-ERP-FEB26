import api from './api'

export const authService = {
  /**
   * Login with email and password
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise} Login response with tokens and user data
   */
  login: (email, password) =>
    api.post('/auth/login', { email, password }).then(res => res.data),
  
  /**
   * Register/Signup with email, password, and full name
   * @param {object} data - Signup data {email, password, full_name}
   * @returns {Promise} Signup response with tokens and user data
   */
  register: (data) =>
    api.post('/auth/signup', { 
      email: data.email, 
      password: data.password, 
      full_name: data.full_name,
      confirm_password: data.password
    }).then(res => res.data),
  
  /**
   * Refresh access token using refresh token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise} New tokens
   */
  refresh: (refreshToken) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }).then(res => res.data),
  
  /**
   * Logout and invalidate tokens
   * @returns {Promise} Logout confirmation
   */
  logout: () =>
    api.post('/auth/logout').then(res => res.data),
  
  /**
   * Get current authenticated user
   * @returns {Promise} User data
   */
  getMe: () =>
    api.get('/auth/me').then(res => res.data),
  
  /**
   * Change user password
   * @param {string} currentPassword - Current password
   * @param {string} newPassword - New password
   * @param {string} confirmPassword - Password confirmation
   * @returns {Promise} Change password confirmation
   */
  changePassword: (currentPassword, newPassword, confirmPassword) =>
    api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    }).then(res => res.data)
}

