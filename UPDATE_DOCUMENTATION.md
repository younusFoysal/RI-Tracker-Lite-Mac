# Auto-Update System Documentation

This document explains how the auto-update system works in the RemoteIntegrity Tracker application and how to create new releases.

## How the Auto-Update System Works

The RemoteIntegrity Tracker application includes an auto-update system that allows users to check for, download, and install updates directly from the application. The system works as follows:

1. **Check for Updates**: When a user clicks the "Check For Updates" button in the Profile page, the application queries the GitHub API to check if a newer version is available.

2. **Update Notification**: If a newer version is available, the user is shown a popup with information about the new version and options to update or cancel.

3. **Download and Install**: If the user chooses to update, the application downloads the new version, installs it, and automatically restarts.

## Creating New Releases

To create a new release that will be detected by the auto-update system, follow these steps:

### 1. Update the Version Number

Update the version number in the following files:

- `backend/main.py`: Update the `APP_VERSION` constant
- `frontend/src/Pages/ProfilePage.jsx`: Update the `appVersion` constant

Make sure both version numbers match.

### 2. Build the Application

Build the application using PyInstaller or your preferred build tool. Make sure to include all necessary files and dependencies.

### 3. Create a GitHub Release

1. Go to your GitHub repository (RemoteIntegrity/RITracker)
2. Click on "Releases" in the right sidebar
3. Click "Draft a new release"
4. Set the tag version to match your application version (e.g., "v1.0.5")
5. Add a title and description for the release
6. Upload the built application as an asset (e.g., RITracker-Setup.exe)
7. Publish the release

### 4. Release Format Requirements

For the auto-update system to work correctly, your GitHub release must follow these requirements:

- The tag name must start with "v" followed by the version number (e.g., "v1.0.5")
- The release must include at least one asset (the installer or executable)
- The asset should be a Windows executable (.exe) or installer (.msi)

## How Version Comparison Works

The application compares version numbers using semantic versioning principles:

- Version numbers are split into components (e.g., "1.0.5" becomes [1, 0, 5])
- Each component is compared numerically
- If the new version has a higher number in any component (starting from the left), it's considered newer
- If versions have different numbers of components, the shorter version is padded with zeros

## Testing the Update System

You can test the update system using the included `test_update.py` script:

```bash
python test_update.py
```

This script tests:
- Version comparison logic
- Checking for updates from GitHub
- Downloading updates (optional)
- Installing updates (simulation only)

## Troubleshooting

If the auto-update system isn't working as expected, check the following:

1. **GitHub Repository Configuration**: Make sure the `GITHUB_REPO` constant in `backend/main.py` is set to the correct repository.

2. **GitHub API Rate Limits**: The GitHub API has rate limits. If you're testing frequently, you might hit these limits.

3. **Release Format**: Ensure your GitHub releases follow the format requirements described above.

4. **Network Connectivity**: The application needs internet access to check for and download updates.

5. **File Permissions**: The application needs permission to write to the download directory and execute the installer.

## Implementation Details

The auto-update system is implemented using the following components:

### Backend (Python)

- `check_for_updates()`: Queries the GitHub API to check for new releases
- `compare_versions()`: Compares version numbers to determine if an update is available
- `download_update()`: Downloads the update file
- `install_update()`: Installs the update and restarts the application

### Frontend (React)

- `UpdatePopup`: Displays update information and options
- `handleCheckForUpdates()`: Initiates the update check process
- `handleUpdate()`: Initiates the download and installation process

The system uses the GitHub API to check for the latest release and download the update file. It supports different types of installers (.exe, .msi) and handles the installation process accordingly.