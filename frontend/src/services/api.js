import axios from 'axios';

const API_URL = 'https://aerostream.onrender.com/api';
// const API_URL = 'http://localhost:8000/api'; // Dev Backup

export default {
    async getFlights() {
        try {
            const response = await axios.get(`${API_URL}/flights`);
            return response.data;
        } catch (error) {
            console.error('Error fetching flights:', error);
            return [];
        }
    },

    async getStats() {
        // Placeholder if stats endpoint isn't ready, or use the real one
        try {
            const response = await axios.get(`${API_URL}/stats`);
            return response.data;
        } catch (error) {
            console.error('Error fetching stats:', error);
            return null;
        }
    }
};
