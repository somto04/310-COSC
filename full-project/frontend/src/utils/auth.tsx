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

export function setAuth(token: string, userId: string, isAdmin: boolean) {
    localStorage.setItem("token", token);
    localStorage.setItem("userId", userId);
    localStorage.setItem("isAdmin", isAdmin ? "true" : "false");
}

export function clearAuth() {
    localStorage.removeItem("token");
    localStorage.removeItem("isAdmin");
    localStorage.removeItem("userId");
}

export function requireAuth(element: React.ReactElement) {
    const token = getToken();

    if (!token) {
        return <Navigate to="/login" replace />;
    }

    return element;
}