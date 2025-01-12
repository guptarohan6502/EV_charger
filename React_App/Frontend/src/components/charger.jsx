import React from 'react';
import ReactApexChart from 'react-apexcharts';
import MyAppBar from './appbar'; // Import your custom AppBar component
import axios from 'axios';
import moment from 'moment-timezone';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import markerImage from './image.png'; // Update path to your marker image
import {
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Box,
    Grid,
    Typography,
} from '@mui/material';

class ChargerDashboard extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            selectedCharger: 'Charger 1', // Default selection
            charger1Series: [],
            charger2Series: [],
            options: {
                chart: {
                    height: 350,
                    type: 'bar',
                    background: '#333',
                },
                plotOptions: {
                    bar: {
                        borderRadius: 10,
                        dataLabels: {
                            position: 'top', // place data labels on top of bars
                        },
                    },
                },
                dataLabels: {
                    enabled: true,
                    formatter: (val) => `${val} kWh`,
                    offsetY: -20,
                    style: {
                        fontSize: '16px',
                        colors: ['#ffffff'],
                    },
                },
                xaxis: {
                    categories: [],
                    labels: {
                        style: {
                            colors: '#ffffff',
                            fontSize: '14px',
                        },
                        // rotate: -45, // optionally rotate labels if overlapping
                    },
                },
                yaxis: {
                    labels: {
                        formatter: (val) => `${val} kWh`,
                        style: {
                            colors: '#ffffff',
                            fontSize: '14px',
                        },
                    },
                },
                title: {
                    text: 'Energy Consumption',
                    align: 'center',
                    offsetY: 10,
                    style: {
                        color: '#ffffff',
                        fontSize: '18px',
                        fontWeight: 'bold',
                    },
                },
                tooltip: {
                    theme: 'dark',
                },
            },
            positions: [
                [17.445289, 78.349593],
                [17.445160, 78.349806],
            ],
        };

        this.updateInterval = null;
    }

    componentDidMount() {
        this.fetchData();
        this.updateInterval = setInterval(this.fetchData, 3600000); // Update data every 1 hour
    }

    componentWillUnmount() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }

    fetchData = async () => {
        try {
            const [charger1Response, charger2Response] = await Promise.all([
                axios.get('http://localhost:8000/charger/get-transactions'),
                axios.get('http://localhost:8000/charger/get-transactions-2'),
            ]);

            const processData = (transactions) => {
                return (
                    transactions
                        // Sort data chronologically
                        .sort((a, b) => a.Timestamp - b.Timestamp)
                        // Take the last 5 data points
                        .slice(-5)
                        .map((item) => ({
                            // Format date as "Jan 10"
                            x: moment.unix(item.Timestamp).tz('Asia/Kolkata').format('MMM DD'),
                            y: item.Units_Consumed || 0,
                        }))
                );
            };

            const charger1Data = processData(charger1Response.data.transactions || []);
            const charger2Data = processData(charger2Response.data.transactions || []);

            this.setState((prevState) => ({
                charger1Series: [{ name: 'Charger 1', data: charger1Data }],
                charger2Series: [{ name: 'Charger 2', data: charger2Data }],
                options: {
                    ...prevState.options,
                    xaxis: {
                        ...prevState.options.xaxis,
                        categories: charger1Data.map((item) => item.x),
                    },
                },
            }));
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    handleChargerChange = (event) => {
        this.setState({ selectedCharger: event.target.value });
    };

    render() {
        const { selectedCharger, charger1Series, charger2Series, options } = this.state;
        // Select the appropriate series based on the selected charger
        const series = selectedCharger === 'Charger 1' ? charger1Series : charger2Series;

        return (
            <Box
                sx={{
                    backgroundColor: '#121212',
                    color: '#fff',
                    minHeight: '100vh',
                }}
            >
                {/* Navbar */}
                <MyAppBar />

                {/* Main Content */}
                <Box sx={{ px: 4, py: 2 }}>
                    {/* Page Title */}
                    <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Charger Dashboard
                    </Typography>

                    {/* Charger Selector */}
                    <FormControl
                        variant="outlined"
                        sx={{
                            mb: 3,
                            minWidth: 220,
                            '& .MuiInputLabel-root': { color: '#fff', fontSize: '16px' },
                            '& .MuiOutlinedInput-root': {
                                color: '#fff',
                                fontSize: '16px',
                                '& fieldset': { borderColor: '#fff' },
                                '&:hover fieldset': { borderColor: '#fff' },
                            },
                            '& .MuiSvgIcon-root': {
                                color: '#fff', // arrow icon color
                            },
                        }}
                    >
                        <InputLabel>Select Charger</InputLabel>
                        <Select
                            value={selectedCharger}
                            onChange={this.handleChargerChange}
                            label="Select Charger"
                        >
                            <MenuItem value="Charger 1">EV-L001-1</MenuItem>
                            <MenuItem value="Charger 2">EV-L001-2</MenuItem>
                        </Select>
                    </FormControl>

                    {/* Grid for Map & Chart */}
                    <Grid container spacing={3}>
                        {/* Map Section */}
                        <Grid item xs={12} md={6}>
                            <Box
                                sx={{
                                    width: '100%',
                                    height: '400px',
                                    border: '1px solid #444',
                                    borderRadius: '8px',
                                    overflow: 'hidden',
                                }}
                            >
                                <MapContainer
                                    center={[17.445289, 78.349593]}
                                    zoom={17}
                                    style={{ width: '100%', height: '100%' }}
                                >
                                    <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                                    {this.state.positions.map((position, index) => (
                                        <Marker
                                            key={index}
                                            position={position}
                                            icon={
                                                new L.Icon({
                                                    iconUrl: markerImage,
                                                    iconSize: [50, 50],
                                                    iconAnchor: [25, 25],
                                                })
                                            }
                                        >
                                            <Popup>{`Charger ${index + 1}`}</Popup>
                                        </Marker>
                                    ))}
                                </MapContainer>
                            </Box>
                        </Grid>

                        {/* Chart Section */}
                        <Grid item xs={12} md={6}>
                            <Box
                                sx={{
                                    width: '100%',
                                    height: '400px',
                                    border: '1px solid #444',
                                    borderRadius: '8px',
                                    p: 2,
                                }}
                            >
                                <ReactApexChart
                                    options={options}
                                    series={series}
                                    type="bar"
                                    height="100%"
                                />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </Box>
        );
    }
}

export default ChargerDashboard;
