import type { Component } from "solid-js";
import { GoogleOAuthProvider } from "../contexts/GoogleOAuthProvider";
import GoogleSignupBtn from "../components/GoogleSignupBtn";
import GoogleLoginBtn from "../components/GoogleLoginBtn";

const googleClientId = import.meta.env.VITE_GOOGLE_OAUTH2_CLIENT_ID;
const googleClientNonce = import.meta.env.VITE_GOOGLE_OAUTH2_NONCE;

const GoogleSignupLogin: Component = () => {
    return (
        <GoogleOAuthProvider
            clientId={googleClientId}
            nonce={googleClientNonce}>
            <GoogleSignupBtn />
            <br />
            <GoogleLoginBtn />
        </GoogleOAuthProvider>
    );
};

export default GoogleSignupLogin;
