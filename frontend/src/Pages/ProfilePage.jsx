import React, { useState, useEffect } from 'react';

// Mock user avatar for demo
const userAvatar = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='32' fill='%236366f1'/%3E%3Ctext x='32' y='40' text-anchor='middle' fill='white' font-family='Arial' font-size='24' font-weight='bold'%3EJD%3C/text%3E%3C/svg%3E";

// --- SVG Icon Components with enhanced styling ---
const IconX = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
);

const IconCheck = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <polyline points="20 6 9 17 4 12"></polyline>
    </svg>
);

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

const IconPencil = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
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

const IconClock = ({ className }) => (
    <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className={className} xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10"></circle>
        <polyline points="12 6 12 12 16 14"></polyline>
    </svg>
);

// Enhanced MenuItem component with animations and modern styling
const MenuItem = ({ icon, text, isLast = false, delay = 0 }) => {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <div
            className={`transform transition-all duration-300 ease-out ${!isLast ? 'mb-2' : ''}`}
            style={{
                animationDelay: `${delay}ms`,
                animation: 'slideInRight 0.6s ease-out forwards'
            }}
        >
            <a
                href="#"
                className="group flex items-center justify-between p-4 rounded-2xl bg-white/70 backdrop-blur-sm border border-white/20 hover:bg-white hover:shadow-lg hover:shadow-indigo-500/10 hover:border-indigo-200/50 text-slate-600 hover:text-slate-800 transition-all duration-300 hover:-translate-y-1"
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
            >
                <div className="flex items-center gap-4">
                    <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-50 to-blue-50 group-hover:from-indigo-100 group-hover:to-blue-100 transition-all duration-300">
                        {React.cloneElement(icon, {
                            className: "h-5 w-5 text-indigo-600 group-hover:text-indigo-700 transition-colors duration-300"
                        })}
                    </div>
                    <span className="font-medium">{text}</span>
                </div>
                <IconArrowRight className={`h-4 w-4 text-slate-400 group-hover:text-indigo-600 transition-all duration-300 ${isHovered ? 'translate-x-1' : ''}`} />
            </a>
        </div>
    );
};

// Status indicator component
const StatusIndicator = () => (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200">
        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
        <span className="text-xs font-medium text-emerald-700">Active</span>
    </div>
);

// Main Profile Page Component
export default function ProfilePage({ user, onClose }) {
    const [mounted, setMounted] = useState(false);

    // Mock user data - replace with your actual user prop
    // const user = {
    //     name: userData?.name,
    //     email: "john.doe@company.com",
    //     avatar: userAvatar,
    //     roleId: {
    //         roleName: "senior developer",
    //         modules: ['Dashboard', 'TimeTracker', 'Reports', 'Projects', 'profile', 'Guides']
    //     }
    // };

    useEffect(() => {
        setMounted(true);
    }, []);

    // List of services the user is being monitored for
    const monitoringItems = user.roleId.modules.filter(item =>
        item !== 'Dashboard' && item !== 'profile' && item !== 'Guides'
    );

    const menuItems = [
        { icon: <IconDashboard />, text: "Go To Dashboard" },
        { icon: <IconInfo />, text: "About RI Tracker" },
        { icon: <IconDownload />, text: "Check For Updates" },
    ];

    return (
        <div className="h-full bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center font-sans">
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
            `}</style>

            <div className={`w-full max-w-md transition-all overflow-hidden duration-700 ease-out ${mounted ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}>
                <div className="bg-white/80 backdrop-blur-xl  shadow-2xl shadow-indigo-500/10 overflow-hidden">

                    {/* Header with gradient background */}
                    <div className="relative bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 p-8 pb-6">
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
                                <StatusIndicator />
                            </div>

                            {/* Enhanced User Info Card */}
                            <div className="bg-white/20 backdrop-blur-sm rounded-2xl p-5 border border-white/30">
                                <div className="flex justify-between items-center ">
                                    <span className="text-white/80 text-sm font-medium">Current Role</span>
                                    <span className="font-bold text-white bg-white/20 backdrop-blur-sm px-3 py-1.5 rounded-xl text-sm capitalize border border-white/30">
                                        {user.roleId.roleName}
                                    </span>
                                </div>
                                {/*<div className="flex items-center gap-3">*/}
                                {/*    <div className="p-2 rounded-xl bg-white/20 backdrop-blur-sm">*/}
                                {/*        <IconClock className="h-4 w-4 text-white" />*/}
                                {/*    </div>*/}
                                {/*    <p className="text-white/90 font-medium text-sm">*/}
                                {/*        RI Tracker is monitoring your work hours*/}
                                {/*    </p>*/}
                                {/*</div>*/}
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
                    <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 p-1 mt-[13px] text-white flex-shrink-0 "></div>
                </div>
            </div>
        </div>
    );
}