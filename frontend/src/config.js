// API Configuration
export const API_BASE_URL = 'http://127.0.0.1:8080/api';

// API Endpoints
export const API_ENDPOINTS = {
  // Resources/Notes
  resources: '/resources',
  resourceById: (id) => `/resources/${id}`,
  resourceRatings: (id) => `/resources/${id}/ratings`,
  resourcesBySubject: (code) => `/subjects/${code}/resources`,
  
  // Courses
  courses: '/courses',
  courseById: (id) => `/course/${id}`,
  courseRoster: (id) => `/course/${id}/roster`,
  professorCourses: (profId) => `/professor/${profId}/courses`,
};

// Helper function to build full URL
export const buildUrl = (endpoint, params = {}) => {
  let url = `${API_BASE_URL}${endpoint}`;
  
  if (Object.keys(params).length > 0) {
    const queryString = new URLSearchParams(params).toString();
    url += `?${queryString}`;
  }
  
  return url;
};
