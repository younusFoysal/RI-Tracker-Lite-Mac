import React, { useState } from 'react';
import { MdEmail, MdLock } from 'react-icons/md';
import logo from "/icon.ico";
import { useAuth } from '../context/AuthContext';

const Logo = () => (
    <img src={logo} alt="RI Lolgo" className="h-16 w-auto" />
);

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const { login } = useAuth();

    // API - POST - https://remotintegrity-auth.vercel.app
    // body -
    // {
    //     "email": "test@test.com",
    //     "password": "123456"
    // }
    // Response -
    // {
    //     "success": true,
    //     "message": "Employee is logged in successfully!",
    //     "data": {
    //     "employee": {
    //         "_id": "68570556049a6f01dd18cda7",
    //             "username": "testuser",
    //             "name": "Test User",
    //             "email": "test@test.com",
    //             "password": "$2b$10$kIgl2agu3ZErLr8BPkODqeH84Qp5L3gT0eZWcu1KeYooxAUGEyJtq",
    //             "avatar": "https://i.ibb.co/ZzLC3NQR/man-Avater.jpg",
    //             "roleId": {
    //             "_id": "685a3458ab3b53d133344a50",
    //                 "roleName": "employee",
    //                 "modules": [
    //                 "Dashboard",
    //                 "workHours",
    //                 "profile",
    //                 "Guides"
    //             ]
    //         },
    //         "employeeId": "687c77e6873a193e1f6cff43",
    //             "role": "user",
    //             "status": "active",
    //             "note": "New User",
    //             "isDeleted": false,
    //             "isBlocked": false,
    //             "needsPasswordChange": false,
    //             "isEmailVerified": false,
    //             "createdAt": "2025-06-21T19:17:42.131Z",
    //             "updatedAt": "2025-07-07T19:07:30.970Z",
    //             "__v": 0,
    //             "division": "",
    //             "position": ""
    //     },
    //     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2ODU3MDU1NjA0OWE2ZjAxZGQxOGNkYTciLCJ1c2VybmFtZSI6InRlc3R1c2VyIiwibmFtZSI6IlRlc3QgVXNlciIsImVtYWlsIjoidGVzdEB0ZXN0LmNvbSIsInJvbGUiOiJ1c2VyIiwiYXZhdGFyIjoiaHR0cHM6Ly9pLmliYi5jby9aekxDM05RUi9tYW4tQXZhdGVyLmpwZyIsInBvc2l0aW9uIjoiIiwicm9sZUlkIjp7Il9pZCI6IjY4NWEzNDU4YWIzYjUzZDEzMzM0NGE1MCIsInJvbGVOYW1lIjoiZW1wbG95ZWUiLCJtb2R1bGVzIjpbIkRhc2hib2FyZCIsIndvcmtIb3VycyIsInByb2ZpbGUiLCJHdWlkZXMiXX0sInN0YXR1cyI6ImFjdGl2ZSIsImlzRGVsZXRlZCI6ZmFsc2UsImlzQmxvY2tlZCI6ZmFsc2UsIm5lZWRzUGFzc3dvcmRDaGFuZ2UiOmZhbHNlLCJpc0VtYWlsVmVyaWZpZWQiOmZhbHNlLCJpYXQiOjE3NTMwOTQ0NzUsImV4cCI6MTc1Mzk1ODQ3NX0.nRrVZLstLbIyHO0sGYP6peVLQ6ZgpJyutLGInM6jEvw",
    //     }
    // }


    const handleLogin = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        
        try {
            const result = await login(email, password);
            if (!result.success) {
                setError(result.message);
            }
            // No need to redirect here as App.jsx will handle conditional rendering
        } catch (err) {
            setError('An unexpected error occurred. Please try again.');
            console.error('Login error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        // Wrapper to center the login card on the page
        <div className="min-h-screen bg-white  flex items-center justify-center ">

            {/* Main Login Card with fixed dimensions */}
            <div className="w-full h-full bg-white rounded-2xl  p-8 flex flex-col justify-between">

                {/* 1. Header Section: Logo and Welcome Text */}
                <div className="text-center">
                    <div className="inline-block mb-4">
                        <Logo />
                    </div>
                    <h2 className="text-3xl font-bold text-blue-900 mb-14">
                        RI Tracker
                    </h2>
                </div>

                {/* 2. Form Section */}
                <form className="space-y-5" onSubmit={handleLogin}>
                    {/* Email Input */}
                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                            Email Address
                        </label>
                        <div className="relative">
                            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                                <MdEmail className="h-5 w-5 text-gray-400" />
                            </div>
                            <input
                                id="email"
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="block w-full rounded-md border-gray-300 pl-10 py-3 text-sm shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                placeholder="you@example.com"
                            />
                        </div>
                    </div>

                    {/* Password Input */}
                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                            Password
                        </label>
                        <div className="relative">
                            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                                <MdLock className="h-5 w-5 text-gray-400" />
                            </div>
                            <input
                                id="password"
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="block w-full rounded-md border-gray-300 pl-10 py-3 text-sm shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                placeholder="Enter your password"
                            />
                        </div>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center">
                            <input
                                id="remember-me"
                                type="checkbox"
                                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                            />
                            <label htmlFor="remember-me" className="ml-2 text-gray-900">
                                Remember me
                            </label>
                        </div>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="text-red-500 text-sm mt-2">
                            {error}
                        </div>
                    )}
                    
                    {/* Submit Button */}
                    <div>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                                isLoading ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-800 hover:bg-blue-700'
                            } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors`}
                        >
                            {isLoading ? 'Logging in...' : 'Log In'}
                        </button>
                    </div>
                </form>


            </div>
        </div>
    );
};

export default Login;