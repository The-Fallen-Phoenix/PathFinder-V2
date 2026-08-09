/**
 * AIpipe Client - Communicates with PathFinder backend AI services
 * Handles all AI-related requests through Flask endpoints
 */

class AIPipeClient {
    constructor() {
        this.baseURL = '/ai';
        this.defaultModel = 'gpt-4o-mini';
    }

    /**
     * Send AI request to backend
     * @param {string} endpoint - API endpoint path
     * @param {object} payload - Request data
     * @returns {Promise<object>} - Response from server
     */
    async request(endpoint, payload) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                return { error: `Server error: ${response.status}` };
            }

            return await response.json();
        } catch (error) {
            return { error: error.message };
        }
    }

    /**
     * Analyze resume against job description
     * @param {string} resume - Resume text
     * @param {string} jobDescription - Job description text
     * @returns {Promise<object>} - Analysis result
     */
    async analyzeResume(resume, jobDescription) {
        return this.request('/analyze-resume', {
            resume: resume,
            job_description: jobDescription
        });
    }

    /**
     * Enhance job listing with AI
     * @param {string} title - Job title
     * @param {string} description - Original description
     * @param {string} budget - Salary/budget info
     * @returns {Promise<object>} - Enhanced description
     */
    async enhanceJobDescription(title, description, budget = 'Competitive') {
        return this.request('/enhance-job', {
            title: title,
            description: description,
            budget: budget
        });
    }

    /**
     * Score an application
     * @param {string} resume - Candidate resume
     * @param {string} requirements - Job requirements
     * @returns {Promise<object>} - Scoring result
     */
    async scoreApplication(resume, requirements) {
        return this.request('/score-app', {
            resume: resume,
            requirements: requirements
        });
    }

    /**
     * Generate interview questions
     * @param {string} jobTitle - Position title
     * @param {string} jobDescription - Job details
     * @param {number} numQuestions - Number of questions to generate
     * @returns {Promise<object>} - Interview questions
     */
    async generateInterviewQuestions(jobTitle, jobDescription, numQuestions = 5) {
        return this.request('/generate-questions', {
            job_title: jobTitle,
            job_description: jobDescription,
            num_questions: numQuestions
        });
    }
}

// Create global instance
const aipipe = new AIPipeClient();

/**
 * Display loading state
 * @param {HTMLElement} element - Target element
 */
function showLoading(element) {
    element.innerHTML = '<div class="loading">Processing...</div>';
}

/**
 * Display AI response
 * @param {HTMLElement} element - Target element
 * @param {object} response - Response object with content or error
 */
function displayAIResponse(element, response) {
    if (response.error) {
        element.innerHTML = `<div class="error">${response.error}</div>`;
    } else {
        element.innerHTML = `<div class="ai-response">${response.content.replace(/\n/g, '<br>')}</div>`;
    }
}
