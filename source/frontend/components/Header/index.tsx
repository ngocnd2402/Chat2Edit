"use client"

import Link from 'next/link';
import { usePathname } from 'next/navigation'
import styles from './header.module.scss';
import routes from '@/utils/routes';

const links = [
    {
        id: 1,
        href: routes.public.index,
        label: 'Home',
    },
    {
        id: 2,
        href: routes.public.chat,
        label: 'Chat',
    },
    {
        id: 3,
        href: routes.public.about,
        label: 'About',
    },
]

const Header = (): JSX.Element => {
    const pathname = usePathname();
    const isActive = (path: string): boolean => pathname === path;

    return (
        <header className={`flex justify-between items-center fixed mx-auto container z-50 ${styles.header}`}>
            <Link href="/">
                <button className={`font-black uppercase text-lg`}>
                    <svg height="32" viewBox="0 0 135 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M10.12 32L0.552 9.6H7.4L15.464 28.992H11.432L19.688 9.6H25.96L16.36 32H10.12ZM31.1113 32V9.6H37.4473V32H31.1113ZM51.619 18.272H62.019V23.008H51.619V18.272ZM52.067 27.104H63.779V32H45.795V9.6H63.363V14.496H52.067V27.104ZM71.135 32V9.6H81.727C84.2017 9.6 86.3777 10.0587 88.255 10.976C90.1323 11.8933 91.5937 13.184 92.639 14.848C93.7057 16.512 94.239 18.496 94.239 20.8C94.239 23.0827 93.7057 25.0667 92.639 26.752C91.5937 28.416 90.1323 29.7067 88.255 30.624C86.3777 31.5413 84.2017 32 81.727 32H71.135ZM77.471 26.944H81.471C82.751 26.944 83.8603 26.7093 84.799 26.24C85.759 25.7493 86.5057 25.0453 87.039 24.128C87.5723 23.1893 87.839 22.08 87.839 20.8C87.839 19.4987 87.5723 18.3893 87.039 17.472C86.5057 16.5547 85.759 15.8613 84.799 15.392C83.8603 14.9013 82.751 14.656 81.471 14.656H77.471V26.944ZM101.413 32V9.6H107.749V32H101.413ZM120.864 32V14.624H113.984V9.6H134.048V14.624H127.2V32H120.864Z" fill="#020008" />
                        <circle cx="34.5" cy="3.5" r="3.5" fill="#020008" />
                        <circle cx="104.5" cy="3.5" r="3.5" fill="#020008" />
                    </svg>
                </button>
            </Link>
            <nav className='flex flex-row gap-4 font-medium py-1 px-2 bg-white rounded-full'>
                {links.map((item) => (
                    <Link key={item.id} href={item.href}>
                        <button className={`${styles.menuButton} capitalize ${isActive(item.href) ? styles.active : ''}`}>
                            {item.href === '/' ? 'home' : item.label}
                        </button>
                    </Link>
                ))}
            </nav>
            <Link href="/login">
                <span className={`${styles.loginButton} rounded-full bg-primary text-white font-medium flex gap-1 items-center`}>
                    <span>Login</span>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M17.9199 6.62C17.8185 6.37565 17.6243 6.18147 17.3799 6.08C17.2597 6.02876 17.1306 6.00158 16.9999 6H6.99994C6.73472 6 6.48037 6.10536 6.29283 6.29289C6.1053 6.48043 5.99994 6.73478 5.99994 7C5.99994 7.26522 6.1053 7.51957 6.29283 7.70711C6.48037 7.89464 6.73472 8 6.99994 8H14.5899L6.28994 16.29C6.19621 16.383 6.12182 16.4936 6.07105 16.6154C6.02028 16.7373 5.99414 16.868 5.99414 17C5.99414 17.132 6.02028 17.2627 6.07105 17.3846C6.12182 17.5064 6.19621 17.617 6.28994 17.71C6.3829 17.8037 6.4935 17.8781 6.61536 17.9289C6.73722 17.9797 6.86793 18.0058 6.99994 18.0058C7.13195 18.0058 7.26266 17.9797 7.38452 17.9289C7.50638 17.8781 7.61698 17.8037 7.70994 17.71L15.9999 9.41V17C15.9999 17.2652 16.1053 17.5196 16.2928 17.7071C16.4804 17.8946 16.7347 18 16.9999 18C17.2652 18 17.5195 17.8946 17.707 17.7071C17.8946 17.5196 17.9999 17.2652 17.9999 17V7C17.9984 6.86932 17.9712 6.74022 17.9199 6.62Z" fill="currentColor"></path>
                    </svg>
                </span>
            </Link>
        </header>
    );
};

export default Header;