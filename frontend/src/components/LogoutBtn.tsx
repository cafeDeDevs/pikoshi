import { type Component } from 'solid-js';
import { useNavigate } from '@solidjs/router';

import urls from '../config/urls';

import { delay } from '../utils/utils';

const LogoutBtn: Component = () => {
    const navigate = useNavigate();
    const logout = async () => {
        try {
            const response = await fetch(urls.BACKEND_AUTH_LOGOUT_ROUTE, {
                method: 'POST',
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
            });
            const jsonRes = await response.json();
            if (!response.ok) throw new Error(jsonRes.message);
            await delay(3000);
            navigate('/');
        } catch (err) {
            const error = err as Error;
            console.error('ERROR :=>', error);
        }
    };
    return <button onClick={logout}>Logout</button>;
};

export default LogoutBtn;
