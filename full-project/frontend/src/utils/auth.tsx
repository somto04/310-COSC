import { Navigate } from "react-router-dom";

export function getToken() {
    return localStorage.getItem("token");
}

export function getIsAdmin() {
    return localStorage.getItem("isAdmin") === "true";
}

export function getUserId() {
    return localStorage.getItem("userId");
}

export function getUsername() {
    return localStorage.getItem("username");
}

export function setAuth(token: string, userId: string, isAdmin: boolean, username: string) {
    localStorage.setItem("token", token);
    localStorage.setItem("userId", userId);
    localStorage.setItem("isAdmin", isAdmin ? "true" : "false");
    localStorage.setItem("username", username);
}

export function clearAuth() {
    localStorage.removeItem("token");
    localStorage.removeItem("isAdmin");
    localStorage.removeItem("userId");
    localStorage.removeItem("username");
}

export function requireAuth(element: React.ReactElement) {
    const token = getToken();

    if (!token) {
        return <Navigate to="/login" replace />;
    }

    return element;
}

export function requireAdmin(element: React.ReactElement) {
    const auth = requireAuth(element);
    
    if (auth !== element) return auth;  // not logged in then redirect

    if (!getIsAdmin()) {
        return <Navigate to="/login" replace />;
    }

    return element;
}