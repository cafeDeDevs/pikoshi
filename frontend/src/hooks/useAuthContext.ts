import urls from "../config/urls";
const useAuthContext = async (): Promise<boolean> => {
    let isAuthenticated = false;
    try {
        const response = await fetch(urls.BACKEND_AUTH_CONTEXT_ROUTE, {
            method: "POST",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            },
            credentials: "include",
        });
        if (!response.ok) {
            const jsonRes = await response.json();
            throw new Error(jsonRes.message);
        }
        isAuthenticated = true;
    } catch (err) {
        const error = err as Error;
        console.error("ERROR :=>", error.message);
    }
    return isAuthenticated;
};

export { useAuthContext };
