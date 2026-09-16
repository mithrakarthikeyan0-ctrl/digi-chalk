// api.js
// Centralized API configuration and WebSocket connection manager

const GATEWAY_URL = localStorage.getItem("GATEWAY_URL");
const API_BASE = GATEWAY_URL ? GATEWAY_URL : "http://127.0.0.1:8000/api/v1";
const WS_BASE = GATEWAY_URL ? GATEWAY_URL.replace(/^http/, "ws") + "/ws" : "ws://127.0.0.1:8000/ws";

// Storage helpers
function getAccessToken() {
    return localStorage.getItem("access_token");
}
function setAccessToken(token) {
    localStorage.setItem("access_token", token);
}
function getRole() {
    return localStorage.getItem("user_role") || "student";
}

// Authenticated fetch wrapper
async function fetchApi(endpoint, options = {}) {
    const token = getAccessToken();
    const headers = {
        "Content-Type": "application/json",
        ...options.headers
    };
    
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });
        
        if (!response.ok) {
            let errData = {};
            try { errData = await response.json(); } catch(e) {}
            throw { status: response.status, data: errData };
        }
        
        // Return null for 204 No Content
        if (response.status === 204) return null;
        
        return await response.json();
    } catch (error) {
        console.error("API Fetch Error:", error);
        throw error;
    }
}

class BoardSocket {
    constructor(sessionId, callbacks = {}) {
        this.sessionId = sessionId;
        this.callbacks = callbacks;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.shouldReconnect = true;
        this.token = getAccessToken();
        
        this.connect();
    }
    
    connect() {
        if (!this.token) {
            console.warn("BoardSocket: No access token available");
            if (this.callbacks.onError) this.callbacks.onError("No access token");
            return;
        }

        if (this.callbacks.onStatus) this.callbacks.onStatus("Connecting...");

        this.ws = new WebSocket(`${WS_BASE}/sessions/${this.sessionId}/board/`);
        
        this.ws.onopen = () => {
            console.log("WebSocket connected, authenticating...");
            this.ws.send(JSON.stringify({
                type: "authenticate",
                token: this.token
            }));
            this.reconnectAttempts = 0;
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                if (data.type === "connected") {
                    console.log("WebSocket authenticated successfully");
                    if (this.callbacks.onStatus) this.callbacks.onStatus("Connected");
                    if (this.callbacks.onConnected) this.callbacks.onConnected(data.role);
                } else if (data.type === "error") {
                    console.error("WebSocket error message:", data.message);
                    if (this.callbacks.onError) this.callbacks.onError(data.message);
                } else {
                    // Pass other messages to consumer
                    if (this.callbacks.onMessage) this.callbacks.onMessage(data);
                }
            } catch (e) {
                console.error("WebSocket message parse error:", e);
            }
        };
        
        this.ws.onclose = (event) => {
            console.log("WebSocket closed");
            if (this.shouldReconnect) {
                if (this.callbacks.onStatus) this.callbacks.onStatus("Reconnecting...");
                const delay = Math.min(1000 * (2 ** this.reconnectAttempts), 10000);
                this.reconnectAttempts++;
                setTimeout(() => this.connect(), delay);
            } else {
                if (this.callbacks.onStatus) this.callbacks.onStatus("Offline");
            }
        };
        
        this.ws.onerror = (error) => {
            console.error("WebSocket transport error");
        };
    }
    
    send(type, payload = {}) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type,
                ...payload
            }));
        }
    }
    
    disconnect() {
        this.shouldReconnect = false;
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}

// API Endpoints
const API = {
    // Auth
    login: (credentials) => fetchApi("/auth/login/", { method: "POST", body: JSON.stringify(credentials) }),
    
    // Dashboards
    getTeacherDashboard: () => fetchApi("/teacher/dashboard/"),
    getTeacherClasses: () => fetchApi("/teacher/classes/"),
    getTeacherClassAttendance: (classId) => fetchApi(`/teacher/classes/${classId}/attendance/`),
    overrideAttendance: (recordId, status, reason) => fetchApi(`/teacher/attendance/${recordId}/override/`, { method: "POST", body: JSON.stringify({status, reason}) }),
    getTeacherSessionEngagement: (sessionId) => fetchApi(`/teacher/sessions/${sessionId}/engagement/`),

    getStudentDashboard: () => fetchApi("/student/dashboard/"),
    getStudentAttendance: () => fetchApi("/student/attendance/"),
    getStudentEngagement: () => fetchApi("/student/engagement/"),

    getParentChildren: () => fetchApi("/parent/children/"),
    getParentChildSummary: (studentId) => fetchApi(`/parent/children/${studentId}/summary/`),
    getParentChildAttendance: (studentId) => fetchApi(`/parent/children/${studentId}/attendance/`),

    getHeadmasterDashboard: () => fetchApi("/headmaster/dashboard/"),
    getHeadmasterClasses: () => fetchApi("/headmaster/classes/"),
    getHeadmasterAttendanceSummary: () => fetchApi("/headmaster/attendance-summary/"),

    // Lessons & Quizzes (Phase 6)
    getLessons: () => fetchApi("/lessons/"),
    getLessonDetail: (lessonId) => fetchApi(`/lessons/${lessonId}/`),
    getReplayProgress: (lessonId) => fetchApi(`/lessons/${lessonId}/progress/`),
    updateReplayProgress: (lessonId, data) => fetchApi(`/lessons/${lessonId}/progress/`, { method: "PUT", body: JSON.stringify(data) }),
    logLearningEvent: (lessonId, data) => fetchApi(`/analytics/student/lessons/${lessonId}/events/`, { method: "POST", body: JSON.stringify(data) }),
    
    getQuizzes: () => fetchApi("/student/quizzes/"),
    getQuizDetail: (quizId) => fetchApi(`/student/quizzes/${quizId}/`),
    startQuizAttempt: (quizId) => fetchApi(`/student/quizzes/${quizId}/attempts/`, { method: "POST" }),
    getQuizAttempt: (attemptId) => fetchApi(`/student/quiz-attempts/${attemptId}/`),
    submitQuizAttempt: (attemptId, answers) => fetchApi(`/student/quiz-attempts/${attemptId}/submit/`, { method: "POST", body: JSON.stringify({answers}) }),

    // EWS
    generateFeatureSnapshot: (studentId, days=30) => fetchApi("/ews/feature-snapshots/generate/", { method: "POST", body: JSON.stringify({student_id: studentId, days}) }),
    trainEWSModel: (versionName) => fetchApi("/ews/train/", { method: "POST", body: JSON.stringify({version_name: versionName}) }),
    runAssessment: (snapshotId) => fetchApi("/ews/assessments/run/", { method: "POST", body: JSON.stringify({snapshot_id: snapshotId}) }),
    getAssessments: () => fetchApi("/ews/assessments/"),
    reviewAssessment: (assessmentId, action) => fetchApi(`/ews/assessments/${assessmentId}/review/`, { method: "POST", body: JSON.stringify({action}) }),
    getInterventions: () => fetchApi("/ews/interventions/"),
    addInterventionNote: (caseId, content) => fetchApi(`/ews/interventions/${caseId}/notes/`, { method: "POST", body: JSON.stringify({content}) }),
    createNotificationDraft: (caseId, recipientType, content) => fetchApi("/ews/notification-drafts/", { method: "POST", body: JSON.stringify({case_id: caseId, recipient_type: recipientType, content}) }),
    approveNotificationDraft: (draftId) => fetchApi(`/ews/notification-drafts/${draftId}/approve/`, { method: "POST" }),

    // Notifications & Communications (Phase 7)
    getCommunicationPreferences: () => fetchApi("/parent/communication-preferences/"),
    updateCommunicationPreferences: (data) => fetchApi("/parent/communication-preferences/", { method: "PUT", body: JSON.stringify(data) }),
    getParentNotifications: () => fetchApi("/parent/notifications/"),
    getTeacherNotificationDrafts: () => fetchApi("/teacher/notifications/drafts/"),
    createTeacherNotificationDraft: (data) => fetchApi("/teacher/notifications/drafts/", { method: "POST", body: JSON.stringify(data) }),
    getPendingNotifications: () => fetchApi("/notifications/pending-approval/"),
    approveNotification: (id) => fetchApi(`/notifications/${id}/approve/`, { method: "POST" }),
    cancelNotification: (id) => fetchApi(`/notifications/${id}/cancel/`, { method: "POST" }),
    sendNotification: (id) => fetchApi(`/notifications/${id}/send/`, { method: "POST" }),
    getNotificationDeliveryHistory: (id) => fetchApi(`/notifications/${id}/delivery-history/`),
};
