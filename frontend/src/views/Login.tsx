import type { Component } from 'solid-js';
import { GoogleOAuthProvider } from '../contexts/GoogleOAuthProvider';
import EmailLogin from '../components/EmailLogin';
import GoogleLoginBtn from '../components/GoogleLoginBtn.tsx';
const googleClientId = import.meta.env.VITE_GOOGLE_OAUTH2_CLIENT_ID;
const googleClientNonce = import.meta.env.VITE_GOOGLE_OAUTH2_NONCE;

const Login: Component = () => {
    return (
        <>
            <p>Login</p>
            <EmailLogin />
            <p>Or Continue with:</p>
            <GoogleOAuthProvider
                clientId={googleClientId}
                nonce={googleClientNonce}>
                <GoogleLoginBtn />
            </GoogleOAuthProvider>
            <br />
            <br />
            <a href='/signup'>Create an account</a>
        </>
    );
};

export default Login;
