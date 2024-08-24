import type { Component } from 'solid-js';
import { GoogleOAuthProvider } from '../contexts/GoogleOAuthProvider';
import EmailSignup from '../components/EmailSignup';
import GoogleSignupBtn from '../components/GoogleSignupBtn.tsx';
const googleClientId = import.meta.env.VITE_GOOGLE_OAUTH2_CLIENT_ID;
const googleClientNonce = import.meta.env.VITE_GOOGLE_OAUTH2_NONCE;

const Signup: Component = () => {
    return (
        <>
            <p>Sign up to continue</p>
            <EmailSignup />
            <p>Or Continue with:</p>
            <GoogleOAuthProvider
                clientId={googleClientId}
                nonce={googleClientNonce}>
                <GoogleSignupBtn />
            </GoogleOAuthProvider>
            <br />
            <br />
            <a href='/login'>Already have a Pikoshi account? Log in</a>
        </>
    );
};

export default Signup;
