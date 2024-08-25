import { createSignal, onMount, Show, type Component } from 'solid-js';
import { useNavigate } from '@solidjs/router';

import urls from '../config/urls';

import { delay, grabStoredCookie } from '../utils/utils';

const Gallery: Component = () => {
    const [isAuthenticated, setIsAuthenticated] = createSignal(false);
    const navigate = useNavigate();
    onMount(async () => {
        try {
            // const csrfToken = grabStoredCookie('csrftoken');
            const response = await fetch(urls.BACKEND_AUTH_CONTEXT_ROUTE, {
                method: 'POST',
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json',
                    // 'X-CSRFToken': csrfToken,
                },
                credentials: 'include',
            });
            const jsonRes = await response.json();
            if (!response.ok) throw new Error(jsonRes.message);
            setIsAuthenticated(true);
        } catch (err) {
            const error = err as Error;
            console.error('ERROR :=>', error);
            await delay(3000);
            navigate('/');
        }
    });

    return (
        <>
            <Show when={isAuthenticated()} fallback={<p>Loading...</p>}>
                <h1>Gallery</h1>
            </Show>
        </>
    );
};

export default Gallery;
