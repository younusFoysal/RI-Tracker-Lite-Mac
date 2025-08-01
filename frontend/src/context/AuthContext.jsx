import React, { createContext, useState, useContext, useEffect } from 'react';
import {toast} from "sonner";

const AuthContext = createContext();
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [currentUser, setCurrentUser] = useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true); // When pywebview is ready AND auth check is done
    const [pywebviewReady, setPywebviewReady] = useState(false); // Only pywebview

    // Listen for pywebview readiness
    useEffect(() => {
        const handleReady = () => setPywebviewReady(true);

        if (window.pywebview) {
            setPywebviewReady(true);
        } else {
            window.addEventListener('pywebviewready', handleReady);
        }

        return () => {
            window.removeEventListener('pywebviewready', handleReady);
        };
    }, []);

    // When pywebview is ready, check authentication
    useEffect(() => {
        const checkAuthStatus = async () => {
            try {
                console.log("Checking authentication status...");
                
                // First, force a reload of auth data from the database
                // This ensures we're working with the latest data
                try {
                    await window.pywebview.api.reload_auth_data();
                    console.log("Forced reload of auth data completed");
                } catch (reloadError) {
                    console.warn("Could not force reload auth data:", reloadError);
                }
                
                const isAuthResponse = await window.pywebview.api.is_authenticated();
                console.log("Auth response:", isAuthResponse);
                
                if (isAuthResponse.authenticated) {
                    console.log("Backend reports authenticated=true");
                    const userResponse = await window.pywebview.api.get_current_user();
                    console.log("User response:", userResponse);
                    
                    if (userResponse.success) {
                        console.log("Setting user and token state");
                        setCurrentUser(userResponse.user);
                        setToken("token-exists");
                    } else {
                        console.error("User data fetch failed despite being authenticated");
                        // Even if we can't get user data, we know we're authenticated
                        // So set token to ensure login screen doesn't show
                        setToken("token-exists");
                    }
                } else {
                    console.log("Not authenticated according to backend");
                    // Ensure token is null to show login screen
                    setToken(null);
                    setCurrentUser(null);
                }
            } catch (error) {
                console.error('Auth check error:', error);
            } finally {
                setLoading(false);
            }
        };

        if (pywebviewReady) {
            checkAuthStatus();
        }
    }, [pywebviewReady]);

    const login = async (email, password, rememberMe = false) => {
        try {
            const response = await window.pywebview.api.login(email, password, rememberMe);
            if (response.success) {
                setCurrentUser(response.data.employee);
                setToken("token-exists");
                return { success: true };
            } else {
                return { success: false, message: response.message || 'Login failed' };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, message: 'An error occurred during login' };
        }
    };

    const logout = async () => {
        try {
            await window.pywebview.api.logout();
            setToken(null);
            setCurrentUser(null);
            toast.success("Logged out successfully!");
        } catch (error) {
            console.error('Logout error:', error);
        }
    };

    const isAuthenticated = () => !!token;

    const getProfile = async () => {
        try {
            if (!isAuthenticated()) return { success: false, message: 'Not authenticated' };
            return await window.pywebview.api.get_profile();
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
        loading,
    };

    return (
        <AuthContext.Provider value={value}>
            {loading ? (
                <div className="w-full h-screen flex items-center justify-center bg-white dark:bg-gray-900">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-500"></div>
                </div>
            ) : (
                children
            )}
        </AuthContext.Provider>
    );
};
