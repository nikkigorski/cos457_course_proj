const API_BASE_URL = 'http://127.0.0.1:8080/api';


/*
CourseAPI: logic to update and delete courses
@author Gage White
@Version 5 December 2025
*/

/**
 * update course
 * @param {number} courseId ID of course to update
 * @param {object} updatedData Object containing course data
 */
export async function updateCourse(courseId, updatedData) {
    const response = await fetch(`${API_BASE_URL}/courses/${courseId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedData),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Failed to update course ${courseId}`);
    }

    return response.json(); 
}

/**
 * Delete a course
 * @param {number} courseId ID of course to delete
 */
export async function deleteCourse(courseId) {
    const response = await fetch(`${API_BASE_URL}/courses/${courseId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Failed to delete course ${courseId}`);
    }
    
    return response.json(); 
}