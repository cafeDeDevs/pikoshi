import { createSignal, Show, type Component } from 'solid-js';

import urls from '../config/urls';
import { validateEmailInput } from '../utils/schema-validators';

const EmailSignup: Component = () => {
    const [email, setEmail] = createSignal<string>('');
    const [message, setMessage] = createSignal<string>('');

    const handleSubmit = async (e: Event) => {
        e.preventDefault();
        try {
            validateEmailInput(email());
            const res = await fetch(urls.BACKEND_SIGNUP_EMAIL_ROUTE, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email() }),
            });
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
                <label for='email-form'>email:</label>
                <br />
                <input
                    type='email'
                    id='email-form'
                    placeholder='johndoe@example.com'
                    style='text-align: center;'
                    value={email()}
                    onChange={e => setEmail(e.target.value)}
                    required
                />
                <br />
                <br />
                <button type='submit'>Continue</button>
            </form>
            <Show when={message().length}>
                <p>{message()}</p>
            </Show>
        </div>
    );
};

export default EmailSignup;
