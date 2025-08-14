import React, { useState, useEffect } from 'react';
import {BsThreeDotsVertical} from "react-icons/bs";
import ProfilePage from './Pages/ProfilePage';
import Login from "./Pages/Login";
import { AuthProvider, useAuth } from './context/AuthContext';
import useAxiosSecure from "./hooks/useAxiosSecure.jsx";
import {QueryClient, QueryClientProvider, useQuery} from "@tanstack/react-query";
import logo from "/icon.ico";
import { Toaster, toast } from 'sonner'


// Expose to Python
window.toastFromPython = (msg, type = "info") => {
    if (type === "success") toast.success(msg);
    else if (type === "error") toast.error(msg);
    else toast(msg);
};


// Compact CSS with modern animations and glassmorphism effects
const compactStyles = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  
  @keyframes rotateSync {
    from { transform: rotate(0deg); }
    to { transform: rotate(720deg); }
  }
  
  @keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 15px rgba(59, 130, 246, 0.3); }
    50% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.6); }
  }
  
  @keyframes slideInUp {
    from { transform: translateY(10px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  @keyframes scaleIn {
    from { transform: scale(0.95); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
  }
  
  .rotate-sync {
    animation: rotateSync 1s linear;
  }
  
  .pulse-glow {
    animation: pulseGlow 2s infinite;
  }
  
  .slide-in-up {
    animation: slideInUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  }
  
  .fade-in {
    animation: fadeIn 0.3s ease-out;
  }
  
  .scale-in {
    animation: scaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  }
  
  .animate-fadeIn {
    animation: fadeIn 0.3s ease-out forwards;
  }
  
  .animate-scaleIn {
    animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }
  
  .glass-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(20px);
  }
  
  .gradient-bg {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .modern-shadow {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
                0 4px 6px -2px rgba(0, 0, 0, 0.05);
  }
  
  .hover-lift {
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  }
  
  .hover-lift:hover {
    transform: translateY(-1px);
    box-shadow: 0 15px 25px -5px rgba(0, 0, 0, 0.15);
  }
  
  .timer-glow {
    position: relative;
  }
  
  .timer-glow::before {
    content: '';
    position: absolute;
    top: -1px;
    left: -1px;
    right: -1px;
    bottom: -1px;
    // background: linear-gradient(45deg, #3b82f6, #8b5cf6, #06b6d4, #10b981);
    background: #002B91;
    border-radius: inherit;
    z-index: -1;
    // filter: blur(6px);
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  .timer-glow.active::before {
    opacity: 0.9;
  }
  
  * {
    font-family: 'Inter', sans-serif;
  }
  
  .app-container {
    width: 400px;
    height: 600px;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }
`;

// Close Icon Component
const IconClose = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
);

// Note Popup Component
const NotePopup = ({ onClose, onSave, initialNote = "" }) => {
    const [note, setNote] = useState(initialNote);
    
    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-fadeIn">
            <div className="bg-white rounded-2xl shadow-xl w-80 overflow-hidden animate-scaleIn">
                <div className="relative p-4 flex justify-end">
                    <button 
                        onClick={onClose}
                        className="p-1 rounded-full hover:bg-gray-100 transition-colors"
                    >
                        <IconClose className="h-5 w-5 text-gray-500" />
                    </button>
                </div>
                <div className="px-6 pb-6 pt-0 flex flex-col">
                    <h2 className="text-xl font-bold text-gray-800 mb-4 text-center">Add Note</h2>
                    <textarea 
                        value={note}
                        onChange={(e) => setNote(e.target.value)}
                        placeholder="What are you working on?"
                        className="w-full border border-gray-300 rounded-lg p-3 mb-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        rows={4}
                    />
                    <button 
                        onClick={() => onSave(note)}
                        className="px-4 py-2 rounded-lg bg-blue-800 hover:bg-blue-700 text-white text-sm font-medium transition-colors"
                    >
                        Save Note
                    </button>
                </div>
            </div>
        </div>
    );
};

// Update Popup Component
const UpdatePopup = ({ 
    appIcon, 
    appName, 
    currentVersion, 
    latestVersion, 
    updateStatus, 
    onClose, 
    onUpdate, 
    downloadProgress 
}) => {
    const currentYear = new Date().getFullYear();
    
    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-fadeIn">
            <div className="bg-white rounded-2xl shadow-xl w-80 overflow-hidden animate-scaleIn">
                <div className="relative p-4 flex justify-end">
                    <button 
                        onClick={onClose}
                        className="p-1 rounded-full hover:bg-gray-100 transition-colors"
                        disabled={updateStatus === 'downloading' || updateStatus === 'installing'}
                    >
                        <IconClose className="h-5 w-5 text-gray-500" />
                    </button>
                </div>
                <div className="px-6 pb-6 pt-0 flex flex-col items-center">
                    <img src={appIcon} alt={appName} className="w-20 h-20 mb-4" />
                    <h2 className="text-xl font-bold text-gray-800 mb-1">{appName}</h2>
                    
                    {updateStatus === 'checking' && (
                        <>
                            <div className="mb-4 flex items-center justify-center">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-800"></div>
                            </div>
                            <p className="text-sm text-gray-600 mb-2 text-center">Checking for updates...</p>
                        </>
                    )}
                    
                    {updateStatus === 'available' && (
                        <>
                            <p className="text-sm text-gray-500 mb-1">Current version: {currentVersion}</p>
                            <p className="text-sm font-medium text-green-600 mb-4">New version available: {latestVersion}</p>
                            <p className="text-sm text-gray-600 mb-4 text-center">Do you want to update?</p>
                            <div className="flex gap-3">
                                <button 
                                    onClick={onClose}
                                    className="px-4 py-1 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium transition-colors"
                                >
                                    No
                                </button>
                                <button 
                                    onClick={onUpdate}
                                    className="px-4 py-1 rounded-lg bg-blue-800 hover:bg-blue-700 text-white text-sm font-medium transition-colors"
                                >
                                    Yes
                                </button>
                            </div>
                        </>
                    )}
                    
                    {updateStatus === 'not-available' && (
                        <>
                            <p className="text-sm text-gray-500 mb-1">Current version: {currentVersion}</p>
                            <p className="text-sm text-gray-600 mb-4 text-center">You are using the latest version.</p>
                        </>
                    )}
                    
                    {updateStatus === 'downloading' && (
                        <>
                            <p className="text-sm text-gray-500 mb-4">Downloading update...</p>
                            <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
                                <div 
                                    className="bg-blue-800 h-2.5 rounded-full transition-all duration-300"
                                    style={{ width: `${downloadProgress}%` }}
                                ></div>
                            </div>
                            <p className="text-xs text-gray-500">{downloadProgress}% complete</p>
                        </>
                    )}
                    
                    {updateStatus === 'installing' && (
                        <>
                            <p className="text-sm text-gray-500 mb-4">Installing update...</p>
                            <div className="mb-4 flex items-center justify-center">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-800"></div>
                            </div>
                            <p className="text-xs text-gray-500">The application will restart automatically.</p>
                        </>
                    )}
                    
                    {updateStatus === 'error' && (
                        <>
                            <p className="text-sm text-red-500 mb-4">Error checking for updates.</p>
                            <button 
                                onClick={onClose}
                                className="px-4 py-2 rounded-lg bg-blue-800 hover:bg-blue-700 text-white text-sm font-medium transition-colors"
                            >
                                OK
                            </button>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

// Compact SVG Icon Components
const IconChevronDown = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <polyline points="6 9 12 15 18 9"></polyline>
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

// Compact Circular Progress
const CircularProgress = ({ percentage, size = "small" }) => {
    const [animatedPercentage, setAnimatedPercentage] = useState(0);

    useEffect(() => {
        const timer = setTimeout(() => {
            setAnimatedPercentage(percentage);
        }, 100);
        return () => clearTimeout(timer);
    }, [percentage]);

    const strokeWidth = size === "small" ? 4 : 6;
    const radius = size === "small" ? 20 : 30;
    const normalizedRadius = radius - strokeWidth * 2;
    const circumference = normalizedRadius * 2 * Math.PI;
    const strokeDashoffset = circumference - (animatedPercentage / 100) * circumference;

    const getColor = (percentage) => {
        if (percentage >= 80) return '#10b981';
        if (percentage >= 60) return '#3b82f6';
        if (percentage >= 40) return '#f59e0b';
        return '#ef4444';
    };

    return (
        <div className={`relative ${size === "small" ? "h-[40px] w-[40px]" : "h-[80px] w-[80px]"} slide-in-up`}>
            <svg
                height="100%"
                width="100%"
                viewBox={`0 0 ${radius*2} ${radius*2}`}
                className="transform -rotate-90"
            >
                <circle
                    stroke="#f1f5f9"
                    fill="transparent"
                    strokeWidth={strokeWidth}
                    r={normalizedRadius}
                    cx={radius}
                    cy={radius}
                />
                <circle
                    stroke={getColor(percentage)}
                    fill="transparent"
                    strokeWidth={strokeWidth}
                    strokeDasharray={circumference + ' ' + circumference}
                    style={{
                        strokeDashoffset,
                        transition: 'stroke-dashoffset 0.8s cubic-bezier(0.16, 1, 0.3, 1)'
                    }}
                    strokeLinecap="round"
                    r={normalizedRadius}
                    cx={radius}
                    cy={radius}
                />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
                <span className={`${size === "small" ? "text-xs" : "text-xs"} font-bold text-gray-700`}>
                    {percentage}%
                </span>
            </div>
        </div>
    );
};

const queryClient = new QueryClient()

// Main App Component with compact design
function AppContent() {
    const [showDropdown, setShowDropdown] = useState(false);
    const [showProjectDropdown, setShowProjectDropdown] = useState(false);
    const [selectedProject, setSelectedProject] = useState('Loading...');
    const [showProfilePage, setShowProfilePage] = useState(false);
    const [isRotating, setIsRotating] = useState(false);
    const { isAuthenticated, logout, currentUser } = useAuth();
    const axiosSecure = useAxiosSecure();
    
    // Update checking state variables
    const [showUpdatePopup, setShowUpdatePopup] = useState(false);
    const [updateStatus, setUpdateStatus] = useState('');
    const [currentVersion, setCurrentVersion] = useState('');
    const [latestVersion, setLatestVersion] = useState('');
    const [downloadUrl, setDownloadUrl] = useState('');
    const [downloadProgress, setDownloadProgress] = useState(0);

    // Projects list
    const projects = ['RemoteIntegrity', 'Sagaya Labs', 'Energy Professionals'];



    // Image Upload API Details
    // POST - https://files.remoteintegrity.com/api/files/5a7f64a1-ab0e-4544-8fcb-4a7b2fc3d428/upload
    // Body - form data - file - image file
    // Headers - x-api-key - 2a978046cf9eebb8f8134281a3e5106d05723cae3eaf8ec58f2596d95feca3de   - Add this key and value in the headers
    // Response -
    // {
    //     "success": true,
    //     "data": {
    //     "url": "https://remoteintegrity.s3.us-east-1.amazonaws.com/tracker_app07-2025/25/user-avatar.png",
    //         "key": "tracker_app07-2025/25/user-avatar.png"
    // },
    //     "message": "File uploaded successfully"
    // }



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
    const [time, setTime] = useState(0);
    const [isRunning, setIsRunning] = useState(false);
    const [sessionInfo, setSessionInfo] = useState(null);
    const [timerError, setTimerError] = useState(null);
    const [isTimerOperationPending, setIsTimerOperationPending] = useState(false);
    
    // State for user note
    const [userNote, setUserNote] = useState("I am working on Task");
    const [showNotePopup, setShowNotePopup] = useState(false);

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
                toast.error("Failed to get stats!");
                console.error("Initial stats fetch error:", error);
            }
        };

        fetchInitialStats();
    }, []);
    
    // Handle checking for updates (used for manual checks from profile page)
    const handleCheckForUpdates = async () => {
        try {
            setShowUpdatePopup(true);
            setUpdateStatus('checking');
            
            // Call backend to check for updates
            const result = await window.pywebview.api.check_for_updates();
            
            if (!result.success) {
                setUpdateStatus('error');
                return;
            }
            
            setCurrentVersion(result.current_version);
            setLatestVersion(result.latest_version);
            
            if (result.update_available) {
                setUpdateStatus('available');
                setDownloadUrl(result.download_url);
            } else {
                setUpdateStatus('not-available');
                // Auto-close the popup after 3 seconds if no update is available
                setTimeout(() => {
                    setShowUpdatePopup(false);
                }, 3000);
            }
        } catch (error) {
            console.error("Error checking for updates:", error);
            setUpdateStatus('error');
        }
    };
    
    // Check for updates on startup - only show popup if update is available
    const checkForUpdatesOnStartup = async () => {
        try {
            // Call backend to check for updates without showing popup
            const result = await window.pywebview.api.check_for_updates();
            
            if (!result.success) {
                console.error("Error checking for updates on startup");
                return;
            }
            
            setCurrentVersion(result.current_version);
            setLatestVersion(result.latest_version);
            
            // Only show popup if an update is available
            if (result.update_available) {
                setShowUpdatePopup(true);
                setUpdateStatus('available');
                setDownloadUrl(result.download_url);
            }
        } catch (error) {
            console.error("Error checking for updates on startup:", error);
        }
    };
    
    // Handle update process
    const handleUpdate = async () => {
        try {
            setUpdateStatus('downloading');
            setDownloadProgress(0);
            
            // Simulate download progress
            const progressInterval = setInterval(() => {
                setDownloadProgress(prev => {
                    if (prev >= 95) {
                        clearInterval(progressInterval);
                        return 95;
                    }
                    return prev + 5;
                });
            }, 300);
            
            // Call backend to download update
            const downloadResult = await window.pywebview.api.download_update(downloadUrl);
            
            clearInterval(progressInterval);
            
            if (!downloadResult.success) {
                setUpdateStatus('error');
                return;
            }
            
            setDownloadProgress(100);
            
            // Short delay to show 100% before installing
            setTimeout(async () => {
                setUpdateStatus('installing');
                
                // Call backend to install update
                const installResult = await window.pywebview.api.install_update(downloadResult.file_path);
                
                if (!installResult.success) {
                    setUpdateStatus('error');
                }
                // No need to handle success case as app will restart
            }, 500);
            
        } catch (error) {
            console.error("Error updating:", error);
            setUpdateStatus('error');
        }
    };
    
    // Effect to check for updates when the app starts
    useEffect(() => {
        // Check for updates when the app starts, but with a slight delay
        // to ensure the app is fully loaded first
        const updateCheckTimer = setTimeout(() => {
            checkForUpdatesOnStartup();
        }, 2000);
        
        return () => clearTimeout(updateCheckTimer);
    }, []);

    // Effect to handle the timer logic
    useEffect(() => {
        let interval = null;
        //let visibilityHiddenTimestamp = null;
        
        if (isRunning) {
            interval = setInterval(() => {
                setTime(prevTime => prevTime + 1);
            }, 1000);

            const handleKeyDown = () => {
                window.pywebview.api.record_keyboard_activity();
            };

            const handleMouseMove = () => {
                window.pywebview.api.record_mouse_activity();
            };

            const handleMouseClick = () => {
                window.pywebview.api.record_mouse_activity();
            };

            // Sync timer with backend when window regains focus
            const handleWindowFocus = async () => {
                try {
                    const result = await window.pywebview.api.get_current_session_time();
                    if (result.success) {
                        setTime(result.elapsed_time);
                    }
                } catch (error) {
                    console.error("Error syncing timer on focus:", error);
                }
            };
            
            // Handle visibility change (for sleep mode detection)
            // const handleVisibilityChange = async () => {
            //     if (document.visibilityState === 'hidden') {
            //         // Page is hidden (could be tab switch or sleep mode)
            //         visibilityHiddenTimestamp = new Date();
            //     } else if (document.visibilityState === 'visible' && visibilityHiddenTimestamp) {
            //         // Page is visible again after being hidden
            //         const hiddenDuration = new Date() - visibilityHiddenTimestamp;
            //         const SLEEP_THRESHOLD_MS = 30000; // 30 seconds threshold to consider it sleep mode
            //
            //         if (hiddenDuration > SLEEP_THRESHOLD_MS) {
            //             // Device was likely in sleep mode, stop the timer
            //             try {
            //                 console.log("Device was in sleep mode for", hiddenDuration / 1000, "seconds. Stopping timer.");
            //                 toast.info("Timer stopped due to device sleep mode");
            //
            //                 const result = await window.pywebview.api.stop_timer();
            //                 if (result.success) {
            //                     setSessionInfo(null);
            //                     setIsRunning(false);
            //                     setTime(0);
            //
            //                     if (result.stats) {
            //                         if (result.stats.daily && result.stats.daily.success) {
            //                             setDailyStats(result.stats.daily.data);
            //                         }
            //                         if (result.stats.weekly && result.stats.weekly.success) {
            //                             setWeeklyStats(result.stats.weekly.data);
            //                         }
            //                         setStatsLastUpdated(new Date());
            //                     }
            //                 } else {
            //                     setTimerError(result.message || "Failed to stop timer after sleep mode");
            //                     console.error("Timer stop error after sleep mode:", result.message);
            //                 }
            //             } catch (error) {
            //                 console.error("Error stopping timer after sleep mode:", error);
            //                 setTimerError("An error occurred while stopping timer after sleep mode");
            //             }
            //         }
            //
            //         visibilityHiddenTimestamp = null;
            //     }
            // };

            window.addEventListener('keydown', handleKeyDown);
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('click', handleMouseClick);
            window.addEventListener('focus', handleWindowFocus);
            // document.addEventListener('visibilitychange', handleVisibilityChange);

            window.pywebview.api.record_mouse_activity();

            return () => {
                clearInterval(interval);
                window.removeEventListener('keydown', handleKeyDown);
                window.removeEventListener('mousemove', handleMouseMove);
                window.removeEventListener('click', handleMouseClick);
                window.removeEventListener('focus', handleWindowFocus);
                // document.removeEventListener('visibilitychange', handleVisibilityChange);
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
        const formattedHours = hours % 12 || 12;

        return `${formattedHours}:${String(minutes).padStart(2, '0')} ${ampm}`;
    };

    // Fetch Employee Details
    const { data: employee = {}, isLoading, refetch } = useQuery({
        queryKey: ['employee'],
        queryFn: async () => {
            const response = await window.pywebview.api.get_profile();
            if (response.success) {
                setSelectedProject(response.data?.companyId?.name);
                return response.data;
            }
            return {};
        }
    });

    const handleCloseProfile = () => {
        setShowProfilePage(false);
    };

    if (showProfilePage) {
        return <ProfilePage user={currentUser} onClose={handleCloseProfile} />;
    }

    // App constants
    const appIcon = logo;
    const appName = "RI Tracker";
    const appVersion = "1.0.15";

    return (
        <div className="app-container gradient-bg">
            <style>{compactStyles}</style>
            
            {/* Update Popup */}
            {showUpdatePopup && (
                <UpdatePopup 
                    appIcon={appIcon}
                    appName={appName}
                    currentVersion={currentVersion}
                    latestVersion={latestVersion}
                    updateStatus={updateStatus}
                    downloadProgress={downloadProgress}
                    onClose={() => {
                        if (updateStatus !== 'downloading' && updateStatus !== 'installing') {
                            setShowUpdatePopup(false);
                        }
                    }}
                    onUpdate={handleUpdate}
                />
            )}

            <div className="h-full glass-card  overflow-hidden modern-shadow fade-in flex flex-col">
                
                {/* Note Popup */}
                {showNotePopup && (
                    <NotePopup 
                        initialNote={userNote}
                        onClose={() => setShowNotePopup(false)}
                        onSave={(note) => {
                            setUserNote(note);
                            setShowNotePopup(false);
                            toast.success("Note saved successfully!");
                        }}
                    />
                )}

                {/* Compact Header */}
                <div className="bg-[#002B91] px-6 pt-4 pb-4 text-white flex-shrink-0">
                {/*<div className="bg-blue-800 p-4 text-white flex-shrink-0">*/}
                    <div className="flex items-center justify-between">
                        <div className="slide-in-up">
                            <h1 className="text-lg font-semibold">RemoteIntegrity Tracker</h1>
                            <p className="text-blue-100 text-xs opacity-90">Track your productivity</p>
                        </div>
                        <div className="relative dropdown-container slide-in-up">
                            <button
                                className="p-1.5 rounded-lg hover:bg-white/20 transition-all duration-200"
                                onClick={() => setShowDropdown(!showDropdown)}
                            >
                                <BsThreeDotsVertical className="h-4 w-4" />
                            </button>
                            {showDropdown && (
                                <div className="absolute top-full right-0 mt-2 w-40 glass-card rounded-lg shadow-xl py-1 z-20 scale-in">
                                    <button
                                        className="block w-full text-left px-3 py-2 text-sm  text-gray-700 hover:bg-blue-50 transition-colors duration-200 flex items-center gap-2"
                                        onClick={() => {
                                            setShowProfilePage(true);
                                            setShowDropdown(false);
                                        }}
                                    >
                                        <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                                        View Profile
                                    </button>
                                    <button
                                        className={`block w-full text-left px-3 py-2 text-sm flex items-center gap-2 ${
                                            isRunning 
                                            ? 'text-red-300 cursor-not-allowed' 
                                            : 'text-red-600 hover:bg-red-50 transition-colors duration-200'
                                        }`}
                                        onClick={() => {
                                            if (!isRunning) {
                                                logout();
                                                setShowDropdown(false);
                                            }
                                        }}
                                        disabled={isRunning}
                                        title={isRunning ? "Stop the timer before logging out" : "Logout"}
                                    >
                                        <div className="w-1.5 h-1.5 bg-red-500 rounded-full"></div>
                                        Logout {isRunning && "(Disabled while timer is running)"}
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto space-y-4 px-6 py-4 ">
                    {/* Compact Project Selection */}
                    <div className="slide-in-up">
                        <div className="mb-3 flex items-center justify-between">
                            <h2 className="text-sm font-semibold text-gray-800 mb-1">Working on</h2>
                            <button 
                                onClick={() => setShowNotePopup(true)}
                                className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-blue-800 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
                            >
                                <span>Add note</span>
                            </button>
                        </div>

                        <div className="relative project-dropdown-container">
                            <button
                                disabled
                                className="w-full glass-card rounded-xl py-3 px-4 transition-all duration-300 hover-lift border border-transparent hover:border-blue-200"
                                onClick={() => setShowProjectDropdown(!showProjectDropdown)}
                            >
                                <div className="flex justify-between items-center">
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-blue-800 rounded-full"></div>
                                        <span className="font-medium text-gray-800 text-sm truncate">{selectedProject}</span>
                                    </div>
                                    <IconChevronDown className="h-4 w-4 text-gray-400 flex-shrink-0" />
                                </div>
                            </button>
                        </div>
                    </div>

                    {/* Compact Timer Section */}
                    <div className={`glass-card rounded-2xl p-4 timer-glow ${isRunning ? 'active pulse-glow' : ''} slide-in-up`}>
                        <div className="flex items-center justify-between">
                            <div className="flex-1">
                                <div className="flex items-end mb-1">
                                    <span className={`text-3xl font-bold ${isRunning ? 'text-white' : "text-gray-800" }  tracking-tight font-mono`}>
                                        {displayTime.h}:{displayTime.m}
                                    </span>
                                    <span className={`text-lg  ml-1 mb-0.5 font-mono ${isRunning ? 'text-gray-100' : "text-gray-400" }`}>
                                        {displayTime.s}
                                    </span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-green-300 animate-pulse' : 'bg-gray-300'} transition-colors duration-300`}></div>
                                    <span className={`text-xs ${isRunning ? 'text-white font-normal' : "text-gray-500 font-medium" } `}>
                                        {isTimerOperationPending ? "Loading..." : isRunning ? 'Active Session' : 'Ready to Start'}
                                    </span>
                                </div>
                            </div>

                            <div className="relative">
                                <button
                                    disabled={isTimerOperationPending}
                                    onClick={async () => {
                                        try {
                                            setTimerError(null);
                                            setIsTimerOperationPending(true);

                                            if (!isRunning) {
                                                const result = await window.pywebview.api.start_timer(selectedProject, userNote);
                                                if (result.success) {
                                                    setSessionInfo(result.data);
                                                    setIsRunning(true);

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
                                                const result = await window.pywebview.api.stop_timer();
                                                if (result.success) {
                                                    setSessionInfo(null);
                                                    setIsRunning(false);
                                                    setTime(0);

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
                                                    // Even if the backend call fails, reset the timer state in the UI
                                                    // This ensures the timer visually stops for the user
                                                    // setSessionInfo(null);
                                                    // setIsRunning(false);
                                                    // setTime(0);
                                                    
                                                    // Show error message
                                                    setTimerError(result.message || "Failed to stop timer");
                                                    console.error("Timer stop error:", result.message);
                                                    
                                                    // Show toast notification
                                                    toast.error("Timer stopped with errors. Some data may not have been saved.");
                                                }
                                            }
                                        } catch (error) {
                                            console.error("Timer operation error:", error);
                                            
                                            // If this was a stop timer operation, ensure the timer is stopped in the UI
                                            // even if an exception occurred
                                            if (isRunning) {
                                                // setSessionInfo(null);
                                                // setIsRunning(false);
                                                // setTime(0);
                                                setTimerError("Failed to stop timer, but timer has been stopped locally");
                                                toast.error("Timer stopped with errors. Some data may not have been saved.");
                                            } else {
                                                setTimerError("An error occurred during timer operation");
                                            }
                                        } finally {
                                            setIsTimerOperationPending(false);
                                        }
                                    }}
                                    className={`group relative w-16 h-16 rounded-xl flex items-center justify-center shadow-lg transition-all duration-300 transform ${
                                        isTimerOperationPending 
                                            ? 'opacity-70 cursor-not-allowed'
                                            : 'hover:scale-105'
                                    } ${
                                        isRunning
                                            ? 'bg-red-400/90 hover:bg-red-500'
                                            : 'bg-blue-800 hover:bg-blue-700'
                                    }`}
                                >
                                    <div className="absolute inset-0 rounded-xl bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                                    {isRunning ? (
                                        <div className="bg-white w-5 h-5 rounded-sm shadow-sm"></div>
                                    ) : (
                                        <div className="w-0 h-0 border-t-[12px] border-t-transparent border-l-[18px] border-l-white border-b-[12px] border-b-transparent ml-0.5 drop-shadow-sm"></div>
                                    )}
                                </button>
                                {timerError && (
                                    <div className="fixed bottom-20 left-6 right-6 mt-2 z-[100]">
                                        <div className="bg-red-50 border border-red-200 text-red-600 text-xs px-4 py-3 rounded-lg shadow-lg max-w-[90%] mx-auto break-words">
                                            {timerError}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Compact Stats Section */}
                    <div className="space-y-3">
                        {/* Today's Stats */}
                        <div className="glass-card rounded-xl p-3 hover-lift slide-in-up">
                            <div className="flex justify-between items-center">
                                <div className="flex-1">
                                    <div className="flex items-center gap-1.5 mb-2">
                                        <div className="w-0.5 h-4 bg-blue-600 rounded-full"></div>
                                        <h3 className="text-gray-600 font-medium text-sm">Today's Progress</h3>
                                    </div>
                                    <div className="space-y-0.5">
                                        <p className="text-xl font-bold text-gray-800">
                                            {dailyStatsTime.hours}
                                            <span className="text-sm font-medium text-gray-500">h</span>
                                            <span className="mx-0.5"></span>
                                            {dailyStatsTime.minutes}
                                            <span className="text-sm font-medium text-gray-500">m</span>
                                        </p>
                                        <p className="text-xs text-gray-500">
                                            {dailyStats.activePercentage || 0}% productive
                                        </p>
                                    </div>
                                </div>
                                <CircularProgress percentage={dailyStats.activePercentage || 0} size="big" />
                            </div>
                        </div>

                        {/* Weekly Stats */}
                        <div className="glass-card rounded-xl p-3 hover-lift slide-in-up">
                            <div className="flex justify-between items-center">
                                <div className="flex-1">
                                    <div className="flex items-center gap-1.5 mb-2">
                                        <div className="w-0.5 h-4 bg-blue-600 rounded-full"></div>
                                        <h3 className="text-gray-600 font-medium text-sm flex items-center gap-1">
                                            This Week
                                            <IconInfo className="text-gray-400 h-3 w-3" />
                                        </h3>
                                    </div>
                                    <div className="space-y-0.5">
                                        <p className="text-xl font-bold text-gray-800">
                                            {weeklyStatsTime.hours}
                                            <span className="text-sm font-medium text-gray-500">h</span>
                                            <span className="mx-0.5"></span>
                                            {weeklyStatsTime.minutes}
                                            <span className="text-sm font-medium text-gray-500">m</span>
                                        </p>
                                        <p className="text-xs text-gray-500">
                                            {weeklyStats.activePercentage || 0}% productive
                                        </p>
                                    </div>
                                </div>
                                <CircularProgress percentage={weeklyStats.activePercentage || 0} size="big" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Compact Footer */}
                <footer className="glass-card border-t border-white/20 py-3 px-6 fade-in flex-shrink-0">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                            <div className="flex items-center gap-1.5">
                                <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></div>
                                <span>Synced</span>
                            </div>
                            <span className="font-medium text-gray-700">
                                {formatLastUpdated(statsLastUpdated)}
                            </span>
                        </div>

                        <button
                            className={`group flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 transition-all duration-300 ${
                                isRotating ? 'pointer-events-none' : 'hover-lift'
                            }`}
                            onClick={async () => {
                                try {
                                    setIsRotating(true);

                                    if (isRunning) {
                                        const activityStats = await window.pywebview.api.get_activity_stats();

                                        if (activityStats.success) {
                                            const sessionUpdateResult = await window.pywebview.api.update_session(
                                                activityStats.active_time,
                                                activityStats.idle_time,
                                                activityStats.keyboard_rate,
                                                activityStats.mouse_rate,
                                                false,
                                                userNote
                                            );

                                            if (!sessionUpdateResult.success) {
                                                console.error("Session update error:", sessionUpdateResult.message);
                                                return;
                                            }
                                        } else {
                                            console.error("Failed to get activity stats:", activityStats.message);
                                            return;
                                        }
                                    }

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
                                    setTimeout(() => {
                                        setIsRotating(false);
                                    }, 1000);
                                }
                            }}
                        >
                            <IconRefreshCw className={`h-3 w-3 text-blue-800 group-hover:text-blue-800 transition-colors duration-200 ${
                                isRotating ? 'rotate-sync' : ''
                            }`} />
                            <span className="text-xs font-medium text-blue-800 group-hover:text-blue-800 transition-colors duration-200">
                                Sync
                            </span>
                        </button>
                    </div>
                </footer>
                <div className="bg-[#002B91] p-1 text-white flex-shrink-0"></div>
            </div>
        </div>
    );
}

// Wrapper component that provides authentication context and conditional rendering
export default function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <AuthProvider>
                <Toaster position="bottom-right" />
                <AuthenticatedApp />
            </AuthProvider>
        </QueryClientProvider>
    );
}

// Component that handles conditional rendering based on authentication status
function AuthenticatedApp() {
    const { isAuthenticated, loading } = useAuth();

    // Enhanced loading screen
    if (loading) {
        return (
            <div className="app-container gradient-bg">
                <div className="h-full glass-card rounded-2xl flex items-center justify-center modern-shadow">
                    <div className="text-center">
                        <div className="w-12 h-12 mx-auto mb-3 relative">
                            <div className="absolute inset-0 rounded-full border-3 border-blue-200"></div>
                            <div className="absolute inset-0 rounded-full border-3 border-blue-800 border-t-transparent animate-spin"></div>
                        </div>
                        <h2 className="text-lg font-semibold text-gray-800 mb-1">TimeSync Pro</h2>
                        <p className="text-gray-600 text-sm">Loading workspace...</p>
                    </div>
                </div>
            </div>
        );
    }

    // Show Login page if not authenticated, otherwise show the app content
    return isAuthenticated() ? <AppContent /> : <Login />;
}