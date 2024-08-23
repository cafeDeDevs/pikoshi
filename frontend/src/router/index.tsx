import App from '../App.tsx';
import TestComponent from '../views/Test';
import EmailRegistrationForm from '../views/EmailRegistration';

const routes = [
    {
        path: '/',
        component: App,
    },
    {
        path: '/test',
        component: TestComponent,
    },
    {
        path: '/email-registration',
        component: EmailRegistrationForm,
    },
];

export default routes;
