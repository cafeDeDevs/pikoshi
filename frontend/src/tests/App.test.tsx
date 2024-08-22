import { describe, it, test, expect } from 'vitest';
import { render } from '@solidjs/testing-library';
import userEvent from '@testing-library/user-event';
import App from '../App';

const user = userEvent.setup();

describe('App', () => {
    test('Renders the App Component And Google Login Button', async () => {
        const { getByRole } = render(() => <App />);
        const googleLoginBtn = getByRole('button');
        expect(googleLoginBtn).toHaveTextContent('Login With Google');
        // await user.click(counter)
    });
});
