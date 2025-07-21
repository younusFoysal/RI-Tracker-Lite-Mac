import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
    return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
    const [currentUser, setCurrentUser] = useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true);

    // Check if user is logged in on initial load
    const checkAuthStatus = async () => {
        try {
            // Use the Python backend to check authentication status
            const isAuthResponse = await window.pywebview.api.is_authenticated();
            
            if (isAuthResponse.authenticated) {
                // Get current user data from Python backend
                const userResponse = await window.pywebview.api.get_current_user();
                
                if (userResponse.success) {
                    setCurrentUser(userResponse.user);
                    setToken("token-exists"); // We don't need the actual token in frontend anymore
                }
            }
        } catch (error) {
            console.error('Auth check error:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkAuthStatus();
    }, []);

    // Login function
    const login = async (email, password) => {
        try {
            // Use the Python backend for login
            const response = await window.pywebview.api.login(email, password);

            if (response.success) {
                // Set user data from response
                setCurrentUser(response.data.employee);
                setToken("token-exists"); // We don't need the actual token in frontend anymore
                return { success: true };
            } else {
                return { success: false, message: response.message || 'Login failed' };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, message: 'An error occurred during login' };
        }
    };

    // Logout function
    const logout = async () => {
        try {
            // Use the Python backend for logout
            await window.pywebview.api.logout();
            setToken(null);
            setCurrentUser(null);
        } catch (error) {
            console.error('Logout error:', error);
        }
    };

    // Check if user is authenticated
    const isAuthenticated = () => {
        return !!token;
    };

    // Get profile data
    const getProfile = async () => {
        try {
            if (!isAuthenticated()) {
                return { success: false, message: 'Not authenticated' };
            }
            
            // Use the Python backend to get profile data
            const response = await window.pywebview.api.get_profile();
            return response;
        } catch (error) {
            console.error('Profile error:', error);
            return { success: false, message: 'An error occurred while fetching profile' };
        }
    };

    const value = {
        currentUser,
        token,
        login,
        logout,
        isAuthenticated,
        getProfile,
        loading
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};