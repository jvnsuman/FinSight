import axiosClient from './axiosClient';

export const financialHealthApi = {
    getHealthScore: async () => {
        const response = await axiosClient.get('/api/financial-health/');
        return response.data;
    },
    
    refreshHealthScore: async () => {
        const response = await axiosClient.post('/api/financial-health/refresh');
        return response.data;
    },
    
    simulateHealthScore: async (overrides, skip_ai = false) => {
        const response = await axiosClient.post('/api/financial-health/simulate', { overrides, skip_ai });
        return response.data;
    },
    
    askHealthCoach: async (question) => {
        const response = await axiosClient.post('/api/financial-health/ask', { question });
        return response.data;
    }
};
