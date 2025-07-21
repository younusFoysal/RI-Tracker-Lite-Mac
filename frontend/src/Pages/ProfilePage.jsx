import React from 'react';

// --- SVG Icon Components (Unchanged) ---
// Using inline SVGs to avoid potential build issues with external libraries.

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


// MenuItem component for cleaner code
const MenuItem = ({ icon, text }) => (
    <a href="#" className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-gray-800 transition-colors">
        <div className="flex items-center gap-4">
            {icon}
            <span>{text}</span>
        </div>
    </a>
);


// Main Profile Page Component
export default function ProfilePage({ user, onClose }) {
    // List of services the user is being monitored for.
    const monitoringItems = user.roleId.modules.filter(item => item !== 'Dashboard' && item !== 'profile' && item !== 'Guides');

    return (
        <div className="bg-gray-50 min-h-screen flex items-center justify-center font-sans">
            <div className="w-full max-w-sm bg-white rounded-2xl  flex flex-col overflow-hidden">

                {/* Header */}
                <header className="p-6">
                    <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center gap-4">
                            {/* User Avatar */}
                            <img
                                src={user.avatar}
                                alt="User Avatar"
                                className="h-16 w-16 rounded-full object-cover border-2 border-indigo-200"
                                // Fallback in case the image link is broken
                                onError={(e) => { e.target.onerror = null; e.target.src = 'https://placehold.co/64x64/E0E7FF/A5B4FC?text=User'; }}
                            />
                            <div>
                                {/* User Name and Email */}
                                <h2 className="font-bold text-lg text-gray-800">{user.name}</h2>
                                <p className="text-sm text-gray-500">{user.email}</p>
                            </div>
                        </div>
                        <button
                            className="text-gray-400 hover:text-gray-600"
                            onClick={onClose}
                        >
                            <IconX className="h-6 w-6" />
                        </button>
                    </div>

                    {/* Plan Card */}
                    <div className="border border-gray-200 rounded-xl p-4 bg-gray-50">
                        <div className="flex justify-between items-center mb-3">
                            <span className="text-gray-500 text-sm">Role</span>
                            {/* User Role, capitalized */}
                            <span className="font-bold text-indigo-700 bg-indigo-100 px-2 py-1 rounded-md text-sm capitalize">{user.roleId.roleName}</span>
                        </div>
                        <p className="text-gray-600 font-semibold mb-3 text-sm">RI Tracker is monitoring your:</p>
                        <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm text-gray-700">
                            {monitoringItems.map(item => (
                                <div key={item} className="flex items-center gap-2">
                                    <IconCheck className="h-5 w-5 text-green-500" />
                                    <span>{item}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </header>

                {/* Menu List */}
                <nav className="flex-grow px-3 pb-3">
                    <MenuItem icon={<IconDashboard className="h-6 w-6 text-gray-400"/>} text="Go To Dashboard" />
                    <MenuItem icon={<IconInfo className="h-6 w-6 text-gray-400"/>} text="About RI Tracker" />
                    <MenuItem icon={<IconDownload className="h-6 w-6 text-gray-400"/>} text="Check For Updates" />
                    <MenuItem icon={<IconPencil className="h-6 w-6 text-gray-400"/>} text="Support" />
                </nav>

                {/* Footer / Sign Out */}
                <footer className="p-3 border-t border-gray-200">

                    <div className="flex items-center justify-center font-bold p-3 rounded-[4px] bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-gray-800 transition-colors">
                        <button className="flex items-center gap-4"
                                onClick={onClose}
                        >
                            <IconSignOut className="h-6 w-6 text-gray-400"/>
                            <span className="text-gray-600">Go Back</span>
                        </button>
                    </div>


                </footer>
            </div>
        </div>
    );
}

