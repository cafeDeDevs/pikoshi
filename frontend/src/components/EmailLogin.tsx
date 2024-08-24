import { createSignal, Show, type Component } from 'solid-js';

import urls from '../config/urls';
import { validateEmailInput } from '../utils/schema-validators';

// TODO: Change to login, not sign up
const EmailLogin: Component = () => {
    const [email, setEmail] = createSignal<string>('');
    const [message, setMessage] = createSignal<string>('');

    const handleSubmit = async (e: Event) => {
        e.preventDefault();
        try {
            validateEmailInput(email());
            const res = await fetch(urls.BACKEND_EMAIL_REGISTRATION_ROUTE, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email() }),
            });
            // TODO: Remove else clause and simply navigate('/onboarding')
            // NOTE: onboarding route not yet implemented
            if (!res.ok) {
                const jsonRes = await res.json();
                throw new Error(jsonRes.message);
            } else {
                const jsonRes = await res.json();
                setMessage(jsonRes.message);
            }
        } catch (err) {
            const error = err as Error;
            console.error('ERROR :=>', error.message);
            setMessage(error.message);
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <label for='email-form' />
                <input
                    type='email'
                    id='email-form'
                    value={email()}
                    onChange={e => setEmail(e.target.value)}
                    required
                />
                <br />
                <button type='submit'>Continue</button>
            </form>
            <Show when={message().length}>
                <p>{message()}</p>
            </Show>
        </div>
    );
};

export default EmailLogin;
