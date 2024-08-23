import type { Component } from 'solid-js';
import { GoogleOAuthProvider } from './contexts/GoogleOAuthProvider';
const googleClientId = import.meta.env.VITE_GOOGLE_OAUTH2_CLIENT_ID;
const googleClientNonce = import.meta.env.VITE_GOOGLE_OAUTH2_NONCE;
import GoogleSignupBtn from './components/GoogleSignupBtn';
import GoogleLoginBtn from './components/GoogleLoginBtn';

import styles from './App.module.css';

const App: Component = () => {
    return (
        <div class={styles.App}>
            <GoogleOAuthProvider
                clientId={googleClientId}
                nonce={googleClientNonce}>
                <GoogleSignupBtn />
                <br />
                <GoogleLoginBtn />
            </GoogleOAuthProvider>
        </div>
    );
};

export default App;
