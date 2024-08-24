import type { Component } from 'solid-js';
import useGoogleLogin from '../hooks/useGoogleLogin';
import { useNavigate } from '@solidjs/router';

import urls from '../config/urls';

const GoogleLoginBtn: Component = () => {
    const navigate = useNavigate();
    const login = useGoogleLogin({
        onSuccess: async (codeResponse): Promise<void> => {
            try {
                const response = await fetch(urls.BACKEND_LOGIN_GOOGLE_ROUTE, {
                    method: 'POST',
                    headers: {
                        Accept: 'application/json',
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        code: codeResponse.code,
                    }),
                });
                if (!response.ok)
                    throw new Error('Error While Authenticating.');
                const jsonResponse = await response.json();
                console.log('jsonResponse :=>', jsonResponse);
                navigate('/test');
            } catch (err) {
                const error = err as Error;
                console.error('ERROR :=>', error);
            }
        },
        onError: errorResponse => {
            console.error('Error :=>', errorResponse);
        },
        flow: 'auth-code', // change to 'implicit' for access_token
    });
    return <button onClick={login}>Google</button>;
};

export default GoogleLoginBtn;
