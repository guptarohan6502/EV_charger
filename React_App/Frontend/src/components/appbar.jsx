import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import MenuItem from '@mui/material/MenuItem';
import AccountCircle from '@mui/icons-material/AccountCircle';
import { useNavigate, useLocation } from 'react-router-dom';
import iiithlogo from './iiithlogo.png';
import scrclogo from './scrclogo.png';

export default function PrimarySearchAppBar() {
    const navigate = useNavigate();
    const location = useLocation();
    const [isHovered, setIsHovered] = React.useState(false);

    // Hover event handlers for the user icon
    const handleMouseEnter = () => setIsHovered(true);
    const handleMouseLeave = () => setIsHovered(false);

    const handleLogout = () => {
        navigate('/'); // Redirect to home page
    };

    // Determine the title based on the current path
    const getTitle = () => {
        if (location.pathname === '/charger') return 'Admin Dashboard';
        if (location.pathname === '/user') return 'User Dashboard';
        return 'Dashboard';
    };

    return (
        <Box sx={{ flexGrow: 1 }}>
            <AppBar
                position="static"
                sx={{
                    backgroundColor: '#05445E',
                }}
            >
                {/*
          Position the Toolbar as 'relative' so we can absolutely position
          the title in the horizontal center.
        */}
                <Toolbar
                    sx={{
                        minHeight: '64px',
                        display: 'flex',
                        alignItems: 'center',
                        position: 'relative',
                    }}
                >
                    {/* Left: Logos */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                        <img
                            src={iiithlogo}
                            alt="IIITH Logo"
                            style={{
                                height: '50px',
                                objectFit: 'contain',
                            }}
                        />
                        <img
                            src={scrclogo}
                            alt="SCRC Logo"
                            style={{
                                height: '50px',
                                objectFit: 'contain',
                            }}
                        />
                    </Box>

                    {/* Center: Page Title (Absolutely Positioned) */}
                    <Typography
                        variant="h5"
                        noWrap
                        component="div"
                        sx={{
                            position: 'absolute',
                            left: '50%',
                            transform: 'translateX(-50%)',
                            fontWeight: 'bold',
                            textAlign: 'center',
                        }}
                    >
                        {getTitle()}
                    </Typography>

                    {/* Right: User Icon & Hover Menu */}
                    <Box
                        sx={{
                            marginLeft: 'auto',
                            position: 'relative',
                            display: 'flex',
                            alignItems: 'center',
                        }}
                        onMouseEnter={handleMouseEnter}
                        onMouseLeave={handleMouseLeave}
                    >
                        <IconButton size="large" color="inherit">
                            <AccountCircle />
                        </IconButton>

                        {isHovered && (
                            <Box
                                sx={{
                                    position: 'absolute',
                                    top: '105%', // Just below the icon
                                    right: 0,   // Align menu to the icon's right edge
                                    backgroundColor: 'black',
                                    boxShadow: 1,
                                    borderRadius: 1,
                                    zIndex: 1000,
                                    minWidth: '150px',
                                }}
                            >
                                <MenuItem>User ID: exampleUser</MenuItem>
                                <MenuItem onClick={handleLogout}>Logout</MenuItem>
                            </Box>
                        )}
                    </Box>
                </Toolbar>
            </AppBar>
        </Box>
    );
}
