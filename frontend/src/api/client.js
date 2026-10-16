import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

/**
 * Extract human-readable error message from Axios error
 */
export const getErrorMessage = (error) => {
  if (error.response && error.response.data && error.response.data.detail) {
    return error.response.data.detail;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

// Books API
export const fetchBooks = async () => {
  const response = await apiClient.get('/books/');
  return response.data;
};

export const fetchBookById = async (bookId) => {
  const response = await apiClient.get(`/books/${bookId}`);
  return response.data;
};

export const createBook = async (bookData) => {
  const response = await apiClient.post('/books/', bookData);
  return response.data;
};

export const reserveBook = async (bookId, userName) => {
  const response = await apiClient.post(`/books/${bookId}/reserve`, {
    user_name: userName,
  });
  return response.data;
};

// Reservations API
export const fetchReservations = async (status = null, bookId = null) => {
  const params = {};
  if (status) params.status = status;
  if (bookId) params.book_id = bookId;
  const response = await apiClient.get('/reservations/', { params });
  return response.data;
};

export const cancelReservation = async (reservationId) => {
  const response = await apiClient.delete(`/reservations/${reservationId}`);
  return response.data;
};

export default apiClient;
