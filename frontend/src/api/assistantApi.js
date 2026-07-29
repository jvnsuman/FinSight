import axiosClient from './axiosClient';

const assistantApi = {
    queryAssistant: async (query) => {
        const response = await axiosClient.post('/assistant/query', { query });
        return response.data;
    }
};

export default assistantApi;
