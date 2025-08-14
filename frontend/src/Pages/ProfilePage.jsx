import React, { useState, useEffect } from 'react';
import userAvatar from '/userAvatar.png'
import logo from "/icon.ico";

// Close Icon Component
const IconClose = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
);

// About Popup Component
const AboutPopup = ({ appIcon, appName, appVersion, onClose }) => {
    const currentYear = new Date().getFullYear();
    
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
                <div className="px-6 pb-6 pt-0 flex flex-col items-center">
                    <img src={appIcon} alt={appName} className="w-20 h-20 mb-4" />
                    <h2 className="text-xl font-bold text-gray-800 mb-1">{appName}</h2>
                    <p className="text-sm text-gray-500 mb-4">Version {appVersion}</p>
                    <p className="text-xs text-gray-400">© {currentYear} {appName}</p>
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
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
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
                            {/*<button */}
                            {/*    onClick={onClose}*/}
                            {/*    className="px-4 py-1 rounded-md bg-blue-800 hover:bg-blue-700 text-white text-sm font-medium transition-colors"*/}
                            {/*>*/}
                            {/*    OK*/}
                            {/*</button>*/}
                        </>
                    )}
                    
                    {updateStatus === 'downloading' && (
                        <>
                            <p className="text-sm text-gray-500 mb-4">Downloading update...</p>
                            <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
                                <div 
                                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" 
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
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                            </div>
                            <p className="text-xs text-gray-500">The application will restart automatically.</p>
                        </>
                    )}
                    
                    {updateStatus === 'error' && (
                        <>
                            <p className="text-sm text-red-500 mb-4">Error checking for updates.</p>
                            <button 
                                onClick={onClose}
                                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors"
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

// --- SVG Icon Components with enhanced styling ---
const IconDashboard = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        <line x1="3" y1="9" x2="21" y2="9"></line>
        <line x1="9" y1="21" x2="9" y2="9"></line>
    </svg>
);

const IconInfo = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="16" x2="12" y2="12"></line>
        <line x1="12" y1="8" x2="12.01" y2="8"></line>
    </svg>
);

const IconDownload = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="7 10 12 15 17 10"></polyline>
        <line x1="12" y1="15" x2="12" y2="3"></line>
    </svg>
);

const IconSignOut = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
        <polyline points="16 17 21 12 16 7"></polyline>
        <line x1="21" y1="12" x2="9" y2="12"></line>
    </svg>
);

const IconArrowRight = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <line x1="5" y1="12" x2="19" y2="12"></line>
        <polyline points="12 5 19 12 12 19"></polyline>
    </svg>
);

// Enhanced MenuItem component with animations and modern styling
const MenuItem = ({ icon, text, isLast = false, delay = 0, onClick }) => {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <div
            className={`transform transition-all duration-300 ease-out ${!isLast ? 'mb-2' : ''}`}
            style={{
                animationDelay: `${delay}ms`,
                animation: 'slideInRight 0.6s ease-out forwards'
            }}
        >
            <div
                className="group flex items-center justify-between p-4 rounded-2xl bg-white/70 backdrop-blur-sm border border-white/20 hover:bg-white hover:shadow-lg hover:shadow-blue-500/10 hover:border-blue-200/50 text-slate-600 hover:text-slate-800 transition-all duration-300 hover:-translate-y-1"
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                onClick={(e) => {
                    e.preventDefault();
                    if (onClick) onClick();
                }}
            >
                <div className="flex items-center gap-4">
                    <div className="p-2 rounded-xl bg-gradient-to-br from-blue-50 to-blue-50 group-hover:from-blue-100 group-hover:to-blue-100 transition-all duration-300">
                        {React.cloneElement(icon, {
                            className: "h-5 w-5 text-blue-600 group-hover:text-blue-700 transition-colors duration-300"
                        })}
                    </div>
                    <span className="font-medium">{text}</span>
                </div>
                <IconArrowRight className={`h-4 w-4 text-slate-400 group-hover:text-blue-600 transition-all duration-300 ${isHovered ? 'translate-x-1' : ''}`} />
            </div>
        </div>
    );
};


// Main Profile Page Component
export default function ProfilePage({ user, onClose }) {
    const [mounted, setMounted] = useState(false);
    const [showAboutPopup, setShowAboutPopup] = useState(false);
    const [showUpdatePopup, setShowUpdatePopup] = useState(false);
    const [updateStatus, setUpdateStatus] = useState('');
    const [currentVersion, setCurrentVersion] = useState('');
    const [latestVersion, setLatestVersion] = useState('');
    const [downloadUrl, setDownloadUrl] = useState('');
    const [downloadProgress, setDownloadProgress] = useState(0);

    useEffect(() => {
        setMounted(true);
    }, []);


    const appIcon = logo;
    const appName = "RI Tracker";
    const appVersion = "1.0.14";

    // Handle menu item clicks
    const handleGoToDashboard = () => {
        window.open("https://app.remoteintegrity.com/dashboard", "_blank");
    };

    const handleAboutRITracker = () => {
        setShowAboutPopup(true);
    };

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
            }
        } catch (error) {
            console.error("Error checking for updates:", error);
            setUpdateStatus('error');
        }
    };
    
    const handleUpdate = async () => {
        try {
            setUpdateStatus('downloading');
            setDownloadProgress(0);
            
            // Simulate download progress (in a real app, you'd get this from the backend)
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

    const menuItems = [
        { icon: <IconDashboard />, text: "Go To Dashboard", onClick: handleGoToDashboard },
        { icon: <IconInfo />, text: "About RI Tracker", onClick: handleAboutRITracker },
        { icon: <IconDownload />, text: "Check For Updates", onClick: handleCheckForUpdates },
    ];

    return (
        <div className="h-full bg-gradient-to-br from-slate-50 via-blue-50 to-blue-100 flex items-center justify-center font-sans">
            <style jsx>{`
                @keyframes slideInDown {
                    from {
                        opacity: 0;
                        transform: translateY(-30px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                @keyframes slideInRight {
                    from {
                        opacity: 0;
                        transform: translateX(30px);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(0);
                    }
                }
                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                @keyframes scaleIn {
                    from {
                        opacity: 0;
                        transform: scale(0.9);
                    }
                    to {
                        opacity: 1;
                        transform: scale(1);
                    }
                }
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                .animate-fadeIn {
                    animation: fadeIn 0.3s ease-out forwards;
                }
                .animate-scaleIn {
                    animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                }
            `}</style>
            
            {/* About Popup */}
            {showAboutPopup && (
                <AboutPopup 
                    appIcon={appIcon}
                    appName={appName}
                    appVersion={appVersion}
                    onClose={() => setShowAboutPopup(false)}
                />
            )}
            
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

            <div className={`w-full max-w-md transition-all overflow-hidden duration-700 ease-out ${mounted ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}>
                <div className="bg-white/80 backdrop-blur-xl  shadow-2xl shadow-blue-500/10 overflow-hidden">

                    {/* Header with background */}
                    <div className="relative bg-[#002B91] p-8 pb-6">
                        {/* Decorative elements */}
                        <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
                        <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>

                        <div
                            className="relative z-10"
                            style={{
                                animation: 'slideInDown 0.8s ease-out forwards'
                            }}
                        >
                            <div className="flex items-start justify-between mb-6">
                                <div className="flex items-center gap-4">
                                    {/* Enhanced User Avatar with ring */}
                                    <div className="relative">
                                        <img
                                            src={user?.avatar || userAvatar}
                                            alt="User Avatar"
                                            className="h-16 w-16 rounded-2xl object-cover border-3 border-white/30 shadow-lg shadow-black/20"
                                            onError={(e) => {
                                                e.target.onerror = null;
                                                e.target.src = userAvatar;
                                            }}
                                        />
                                        <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-emerald-500 rounded-full border-2 border-white shadow-sm"></div>
                                    </div>
                                    <div>
                                        <h2 className="font-bold text-xl text-white mb-1">{user.name}</h2>
                                        <p className="text-white/80 text-sm font-medium">{user.email}</p>
                                    </div>
                                </div>
                            </div>

                            {/* Enhanced User Info Card */}
                            <div className="bg-white/20 backdrop-blur-sm rounded-2xl p-5 border border-white/30">
                                <div className="flex justify-between items-center ">
                                    <span className="text-white/80 text-sm font-medium">Current Role</span>
                                    <span className="font-bold text-white bg-white/20 backdrop-blur-sm px-3 py-1.5 rounded-xl text-sm capitalize border border-white/30">
                                        {user.roleId.roleName}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Menu List with staggered animations */}
                    <nav className="p-6 space-y-0">
                        {menuItems.map((item, index) => (
                            <MenuItem
                                key={index}
                                icon={item.icon}
                                text={item.text}
                                isLast={index === menuItems.length - 1}
                                delay={index * 100}
                                onClick={item.onClick}
                            />
                        ))}
                    </nav>

                    {/* Enhanced Footer */}
                    <div className="p-6 pt-0">
                        <div
                            className="relative group"
                            style={{
                                animation: 'fadeInUp 0.8s ease-out forwards',
                                animationDelay: '400ms',
                                animationFillMode: 'both'
                            }}
                        >
                            <button
                                className="w-full flex items-center justify-center gap-3 p-4 rounded-2xl bg-gradient-to-r from-slate-100 to-slate-50 hover:from-slate-200 hover:to-slate-100 border border-slate-200/50 hover:border-slate-300/50 text-slate-600 hover:text-slate-800 transition-all duration-300 group-hover:shadow-lg group-hover:shadow-slate-500/10 group-hover:-translate-y-0.5"
                                onClick={onClose}
                            >
                                <div className="p-1.5 rounded-lg bg-slate-200/50 group-hover:bg-slate-300/50 transition-colors duration-300">
                                    <IconSignOut className="h-4 w-4" />
                                </div>
                                <span className="font-semibold">Go Back</span>
                                <div className="ml-auto opacity-50 group-hover:opacity-100 transition-opacity duration-300">
                                    <IconArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform duration-300" />
                                </div>
                            </button>
                        </div>
                    </div>
                    <div className="bg-[#002B91] p-1 mt-[13px] text-white flex-shrink-0 "></div>
                </div>
            </div>
        </div>
    );
}