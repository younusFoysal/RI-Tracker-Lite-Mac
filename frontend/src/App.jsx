import React, { useState, useEffect } from 'react';
import {BsThreeDotsVertical} from "react-icons/bs";
import ProfilePage from './Pages/ProfilePage';
import Login from "./Pages/Login";
import { AuthProvider, useAuth } from './context/AuthContext';
import useAxiosSecure from "./hooks/useAxiosSecure.jsx";
import {QueryClient, QueryClientProvider, useMutation, useQuery} from "@tanstack/react-query";

// --- SVG Icon Components ---
// These components replace the react-icons dependency to avoid build issues.

const IconBuffer = ({ className }) => (
    <svg viewBox="0 0 20 20" fill="currentColor" className={className}>
        <path d="M2 4a2 2 0 012-2h12a2 2 0 012 2v2a2 2 0 01-2 2H4a2 2 0 01-2-2V4z"></path>
        <path d="M2 10a2 2 0 012-2h12a2 2 0 012 2v2a2 2 0 01-2 2H4a2 2 0 01-2-2v-2z"></path>
    </svg>
);

const IconMinus = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <line x1="5" y1="12" x2="19" y2="12"></line>
    </svg>
);

const IconSquare = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
    </svg>
);

const IconX = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
);

const IconChevronDown = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <polyline points="6 9 12 15 18 9"></polyline>
    </svg>
);

const IconClipboard = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
        <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
    </svg>
);

const IconInfo = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="16" x2="12" y2="12"></line>
        <line x1="12" y1="8" x2="12.01" y2="8"></line>
    </svg>
);

const IconRefreshCw = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <polyline points="23 4 23 10 17 10"></polyline>
        <polyline points="1 20 1 14 7 14"></polyline>
        <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
    </svg>
);

const IconChevronsLeft = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <polyline points="11 17 6 12 11 7"></polyline>
        <polyline points="18 17 13 12 18 7"></polyline>
    </svg>
);


// A component for the circular progress bar
const CircularProgress = ({ percentage }) => {
    const strokeWidth = 10;
    const radius = 50;
    const normalizedRadius = radius - strokeWidth * 2;
    const circumference = normalizedRadius * 2 * Math.PI;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;

    return (
        <div className="relative h-[100px] w-[100px]">
            <svg
                height="100%"
                width="100%"
                viewBox={`0 0 ${radius*2} ${radius*2}`}
                className="transform -rotate-90"
            >
                <circle
                    stroke="#e6e6e6"
                    fill="transparent"
                    strokeWidth={strokeWidth}
                    r={normalizedRadius}
                    cx={radius}
                    cy={radius}
                />
                <circle
                    stroke="#002B91"
                    fill="transparent"
                    strokeWidth={strokeWidth}
                    strokeDasharray={circumference + ' ' + circumference}
                    style={{ strokeDashoffset }}
                    strokeLinecap="round"
                    r={normalizedRadius}
                    cx={radius}
                    cy={radius}
                />
            </svg>
            <span className="absolute text-xl font-bold text-gray-700 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                {percentage}%
            </span>
        </div>
    );
};


const queryClient = new QueryClient()

// Main App Component
function AppContent() {
    const [activeTab, setActiveTab] = useState('tracker');
    const [showDropdown, setShowDropdown] = useState(false);
    const [showProjectDropdown, setShowProjectDropdown] = useState(false);
    const [selectedProject, setSelectedProject] = useState('Loading...');
    const [showProfilePage, setShowProfilePage] = useState(false);
    const [isRotating, setIsRotating] = useState(false);

    const { isAuthenticated, logout, currentUser } = useAuth();
    const axiosSecure = useAxiosSecure()

    console.log(currentUser);
    
    // Projects list
    const projects = ['RemoteIntegrity', 'Sagaya Labs', 'Energy Professionals'];
    
    // Close dropdowns when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (showDropdown && !event.target.closest('.dropdown-container')) {
                setShowDropdown(false);
            }
            if (showProjectDropdown && !event.target.closest('.project-dropdown-container')) {
                setShowProjectDropdown(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [showDropdown, showProjectDropdown]);

    // State for the timer
    const [time, setTime] = useState(0); // Initial time in seconds
    const [isRunning, setIsRunning] = useState(false);
    const [sessionInfo, setSessionInfo] = useState(null);
    const [timerError, setTimerError] = useState(null);
    
    // State for stats
    const [dailyStats, setDailyStats] = useState({
        totalHours: 0,
        activeHours: 0,
        activePercentage: 0
    });
    const [weeklyStats, setWeeklyStats] = useState({
        totalHours: 0,
        activeHours: 0,
        activePercentage: 0
    });
    const [statsLastUpdated, setStatsLastUpdated] = useState(null);

    // Effect to fetch stats when the app is opened
    useEffect(() => {
        const fetchInitialStats = async () => {
            try {
                // Get updated stats
                const dailyResult = await window.pywebview.api.get_daily_stats();
                const weeklyResult = await window.pywebview.api.get_weekly_stats();
                
                if (dailyResult.success) {
                    setDailyStats(dailyResult.data);
                }
                
                if (weeklyResult.success) {
                    setWeeklyStats(weeklyResult.data);
                }
                
                setStatsLastUpdated(new Date());
            } catch (error) {
                console.error("Initial stats fetch error:", error);
            }
        };
        
        // Fetch stats when component mounts
        fetchInitialStats();
    }, []);
    
    // Effect to handle the timer logic
    useEffect(() => {
        let interval = null;
        if (isRunning) {
            interval = setInterval(() => {
                setTime(prevTime => prevTime + 1);
            }, 1000);
            
            // Add event listeners for activity tracking
            const handleKeyDown = () => {
                window.pywebview.api.record_keyboard_activity();
            };
            
            const handleMouseMove = () => {
                window.pywebview.api.record_mouse_activity();
            };
            
            const handleMouseClick = () => {
                window.pywebview.api.record_mouse_activity();
            };
            
            // Add event listeners
            window.addEventListener('keydown', handleKeyDown);
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('click', handleMouseClick);
            
            // Initial activity recording
            window.pywebview.api.record_mouse_activity();
            
            // Return cleanup function
            return () => {
                clearInterval(interval);
                window.removeEventListener('keydown', handleKeyDown);
                window.removeEventListener('mousemove', handleMouseMove);
                window.removeEventListener('click', handleMouseClick);
            };
        } else {
            clearInterval(interval);
        }
        return () => clearInterval(interval);
    }, [isRunning]);

    // Format time from seconds to HH:MM:SS
    const formatTime = (seconds) => {
        const h = String(Math.floor(seconds / 3600)).padStart(2, '0');
        const m = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
        const s = String(seconds % 60).padStart(2, '0');
        return { h, m, s };
    };

    // Format stats time from seconds to hours and minutes
    const formatStatsTime = (seconds) => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return {
            hours: String(hours).padStart(2, '0'),
            minutes: String(minutes).padStart(2, '0')
        };
    };

    const displayTime = formatTime(time);
    const dailyStatsTime = formatStatsTime(dailyStats.totalHours || 0);
    const weeklyStatsTime = formatStatsTime(weeklyStats.totalHours || 0);
    
    // Format last updated time
    const formatLastUpdated = (date) => {
        if (!date) return 'Never';
        
        const hours = date.getHours();
        const minutes = date.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        const formattedHours = hours % 12 || 12; // Convert 0 to 12 for 12 AM
        
        return `${formattedHours}:${String(minutes).padStart(2, '0')} ${ampm}`;
    };




    // Fetch Employee Details
    const { data: employee = {}, isLoading, refetch } = useQuery({
        queryKey: ['employee'],
        queryFn: async () => {
            // Use the getProfile method from AuthContext instead of direct API call
            const response = await window.pywebview.api.get_profile();
            if (response.success) {
                setSelectedProject(response.data?.companyId?.name);
                return response.data;
            }
            return {};
        }
    });

    console.log(employee);
    // employee id
    console.log(currentUser?.employeeId);

    // Company id
    console.log(employee?.companyId?._id);



    // send session
    // API - POST - PATCH - https://tracker-beta-kohl.vercel.app/api/v1/sessions/ - With Bearer Token
    // Body -
    // {
    //     "employeeId": "687c77e6873a193e1f6cff43",
    //     "companyId": "6852cf7cb225521271b2452d",
    //     "startTime": "2025-06-29T08:00:00.000Z",     // UTC
    //     "endTime": "2025-06-29T10:00:00.000Z",       // UTC
    //     "activeTime": 90,  // Second
    //     "idleTime": 30,   // Second
    //     "keyboardActivityRate": 100,   // Second
    //     "mouseActivityRate": 1200,    // Second
    //     "notes": "Session from RI Tracker APP v1."
    // }
    // Response -
    // {
    //     "success": true,
    //     "message": "Session created successfully",
    //     "data": {
    //     "employeeId": "687c77e6873a193e1f6cff43",
    //         "companyId": "6852cf7cb225521271b2452d",
    //         "startTime": "2025-06-29T08:00:00.000Z",
    //         "endTime": "2025-06-29T10:00:00.000Z",
    //         "activeTime": 90,
    //         "idleTime": 30,
    //         "notes": "Session from Postman.",
    //         "timezone": "UTC",
    //         "isDeleted": false,
    //         "mouseActivityRate": 1200,
    //         "keyboardActivityRate": 100,
    //         "_id": "687eab67026f5aab54d69cd2",
    //         "createdAt": "2025-07-21T21:04:39.235Z",
    //         "updatedAt": "2025-07-21T21:04:39.235Z",
    //         "__v": 0
    // }
    // }


    // Get Daily Stats of Employee
    // API - GET - https://tracker-beta-kohl.vercel.app/api/v1/stats/daily/{employee id} - With Bearer Token
    // Response -
    // {
    //     "success": true,
    //     "message": "Daily stats retrieved successfully",
    //     "data": {
    //     "date": "2025-07-22",
    //         "totalHours": 158,  // Second
    //         "activeHours": 135,  // Second
    //         "idleHours": 23,   // Second
    //         "activePercentage": 85,
    //         "sessionCount": 1
    // }
    // }

    // Get Weekly Stats of Employee
    // API - GET - https://tracker-beta-kohl.vercel.app/api/v1/stats/weekly/{employee id} - With Bearer Token
    // Response -
    // {
    //     "success": true,
    //     "message": "Weekly stats retrieved successfully",
    //     "data": {
    //     "weekStart": "2025-07-20T00:00:00.000Z",
    //         "weekEnd": "2025-07-26T23:59:59.999Z",
    //         "totalHours": 9056,  // Second
    //         "activeHours": 7953,  // Second
    //         "idleHours": 1103,   // Second
    //         "activePercentage": 88,
    //         "averageSessionsPerDay": 3
    // }
    // }




    // Function to handle returning from profile page
    const handleCloseProfile = () => {
        setShowProfilePage(false);
    };

    // If profile page is shown, render it
    if (showProfilePage) {
        return <ProfilePage user={currentUser}  onClose={handleCloseProfile} />;
    }

    return (
        <div className="min-h-screen flex items-center justify-center font-sans">
            <div className="w-full max-w-sm bg-gray-50 rounded-lg overflow-hidden">

                <main className="p-6 space-y-6">
                    {/* Project Selection Section */}
                    <div>
                        <h2 className="text-lg font-semibold text-gray-800 mb-4">What are you working on?</h2>
                        <div className="space-y-3">
                            <div className="relative project-dropdown-container">
                                <button
                                    disabled
                                    className="w-full flex justify-between items-center bg-white border border-gray-300 rounded-md py-3 px-4 leading-tight focus:outline-none focus:border-blue-800 focus:ring-1 focus:ring-blue-800"
                                    onClick={() => setShowProjectDropdown(!showProjectDropdown)}
                                >
                                    <span>{selectedProject}</span>
                                    <IconChevronDown className="h-5 w-5 text-gray-700" />
                                </button>
                                {showProjectDropdown && (
                                    <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-md shadow-lg py-1 z-10 border border-gray-200">
                                        {projects.map((project, index) => (
                                            <button 
                                                key={index}
                                                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                onClick={() => {
                                                    setSelectedProject(project);
                                                    setShowProjectDropdown(false);
                                                }}
                                            >
                                                {project}
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Timer Section */}
                    <div className="bg-white border-2 border-blue-800 rounded-xl p-4 flex items-center justify-between shadow-sm">
                        <div className="flex items-end">
                            <span className="text-5xl font-bold text-gray-800 tracking-wider">{displayTime.h}:{displayTime.m}</span>
                            <span className="text-2xl text-gray-500 ml-1 mb-1">{displayTime.s}</span>
                        </div>
                        <div className="relative">
                            <button
                                onClick={async () => {
                                    try {
                                        setTimerError(null);
                                        
                                        if (!isRunning) {
                                            // Start the timer
                                            const result = await window.pywebview.api.start_timer(selectedProject);
                                            if (result.success) {
                                                setSessionInfo(result.data);
                                                setIsRunning(true);
                                                
                                                // Update stats if available
                                                if (result.stats) {
                                                    if (result.stats.daily && result.stats.daily.success) {
                                                        setDailyStats(result.stats.daily.data);
                                                    }
                                                    if (result.stats.weekly && result.stats.weekly.success) {
                                                        setWeeklyStats(result.stats.weekly.data);
                                                    }
                                                    setStatsLastUpdated(new Date());
                                                }
                                            } else {
                                                setTimerError(result.message || "Failed to start timer");
                                                console.error("Timer start error:", result.message);
                                            }
                                        } else {
                                            // Stop the timer
                                            const result = await window.pywebview.api.stop_timer();
                                            if (result.success) {
                                                setSessionInfo(null);
                                                setIsRunning(false);
                                                setTime(0); // Reset timer to 0
                                                
                                                // Update stats if available
                                                if (result.stats) {
                                                    if (result.stats.daily && result.stats.daily.success) {
                                                        setDailyStats(result.stats.daily.data);
                                                    }
                                                    if (result.stats.weekly && result.stats.weekly.success) {
                                                        setWeeklyStats(result.stats.weekly.data);
                                                    }
                                                    setStatsLastUpdated(new Date());
                                                }
                                            } else {
                                                setTimerError(result.message || "Failed to stop timer");
                                                console.error("Timer stop error:", result.message);
                                            }
                                        }
                                    } catch (error) {
                                        console.error("Timer operation error:", error);
                                        setTimerError("An error occurred during timer operation");
                                    }
                                }}
                                className={`w-16 h-16 rounded-full flex items-center justify-center shadow-md transition-colors ${isRunning ? 'bg-red-500 hover:bg-red-600' : 'bg-[#002B91] hover:bg-blue-800'}`}
                            >
                                {isRunning ? (
                                    <div className="bg-white w-6 h-6 rounded-md"></div>
                                ) : (
                                    <div className="w-0 h-0 border-t-[12px] border-t-transparent border-l-[20px] border-l-white border-b-[12px] border-b-transparent ml-1"></div>
                                )}
                            </button>
                            {timerError && (
                                <div className="absolute top-full right-0 mt-2 text-xs text-red-500">
                                    {timerError}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Stats Section */}
                    <div className="space-y-4">
                        <div className="bg-white p-4 rounded-xl shadow-sm flex justify-between items-center">
                            <div>
                                <p className="text-gray-500">Today</p>
                                <p className="text-2xl font-bold text-gray-800">
                                    {dailyStatsTime.hours}<span className="text-lg">h</span> {dailyStatsTime.minutes}<span className="text-lg">m</span>
                                </p>
                            </div>
                            <CircularProgress percentage={dailyStats.activePercentage || 0} />
                        </div>
                        <div className="bg-white p-4 rounded-xl shadow-sm flex justify-between items-center">
                            <div>
                                <p className="text-gray-500 flex items-center gap-1">
                                    This Week
                                    <IconInfo className="text-gray-400 h-4 w-4" />
                                </p>
                                <p className="text-2xl font-bold text-gray-800">
                                    {weeklyStatsTime.hours}<span className="text-lg">h</span> {weeklyStatsTime.minutes}<span className="text-lg">m</span>
                                </p>
                            </div>
                            <CircularProgress percentage={weeklyStats.activePercentage || 0} />
                        </div>
                    </div>
                </main>

                {/* Footer */}
                <footer className="bg-white p-3 flex justify-between items-center text-sm text-gray-500 border-t border-gray-200 relative">
                    <div className="relative dropdown-container">
                        <button 
                            className="p-2 rounded-md hover:bg-gray-100"
                            onClick={() => setShowDropdown(!showDropdown)}
                        >
                            <BsThreeDotsVertical className="h-5 w-5" />
                        </button>
                        {showDropdown && (
                            <div className="absolute bottom-full left-0 mb-2 w-48 bg-white rounded-md shadow-lg py-1 z-10 border border-gray-200">
                                <button 
                                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                    onClick={() => {
                                        setShowProfilePage(true);
                                        setShowDropdown(false);
                                    }}
                                >
                                    View Profile
                                </button>
                                <button 
                                    className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                                    onClick={() => {
                                        logout();
                                        setShowDropdown(false);
                                    }}
                                >
                                    Logout
                                </button>
                            </div>
                        )}
                    </div>
                    <span>Last updated at {formatLastUpdated(statsLastUpdated)}</span>
                    <button
                        className={`flex items-center gap-2 p-2 rounded-md hover:bg-gray-100 ${isRotating ? 'pointer-events-none' : ''}`}
                        onClick={async () => {
                            try {
                                // Start rotation animation
                                setIsRotating(true);

                                // Get updated stats
                                const dailyResult = await window.pywebview.api.get_daily_stats();
                                const weeklyResult = await window.pywebview.api.get_weekly_stats();
                                
                                if (dailyResult.success) {
                                    setDailyStats(dailyResult.data);
                                }
                                
                                if (weeklyResult.success) {
                                    setWeeklyStats(weeklyResult.data);
                                }
                                
                                setStatsLastUpdated(new Date());
                            } catch (error) {
                                console.error("Stats sync error:", error);
                            } finally {
                                // Stop rotation animation after a delay to complete the animation
                                setTimeout(() => {
                                    setIsRotating(false);
                                }, 1000); // 1 second to match the animation duration
                            }
                        }}
                    >
                        <IconRefreshCw  className={`h-4 w-4 ${isRotating ? 'animate-spin-fast' : ''}`} />
                        <span>Sync</span>
                    </button>
                </footer>

            </div>

        </div>
    );
}

// Wrapper component that provides authentication context and conditional rendering
export default function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <AuthProvider>
                <AuthenticatedApp />
            </AuthProvider>
        </QueryClientProvider>
    );
}

// Component that handles conditional rendering based on authentication status
function AuthenticatedApp() {
    const { isAuthenticated, loading } = useAuth();
    
    // Show loading indicator while checking authentication status
    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <p className="text-gray-600">Loading...</p>
            </div>
        );
    }
    
    // Show Login page if not authenticated, otherwise show the app content
    return isAuthenticated() ? <AppContent /> : <Login />;
}
