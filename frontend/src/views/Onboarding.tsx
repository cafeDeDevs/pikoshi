import { type Component } from 'solid-js';
import { useLocation } from '@solidjs/router';

const Onboarding: Component = () => {
    const location = useLocation();

    const queryParams = new URLSearchParams(location.search);
    const token = queryParams.get('token');
    console.log('token :=>', token);
    return (
        <>
            <h1>Onboarding Goes Here</h1>
        </>
    );
};

export default Onboarding;
