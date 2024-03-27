import React, { useState } from 'react';

const MenuButton: React.FC = () => {
    const [isActive, setIsActive] = useState(false);

    const toggleMenu = () => {
        setIsActive(!isActive);
    };

    return (
        <div className={`p-4 cursor-pointer hover:bg-background rounded-full text-white ${isActive ? 'change' : ''}`} onClick={toggleMenu}>
            <div className={`bg-gray-500 rounded-full h-[2px] w-5 my-1 transition duration-300 ease-in-out ${isActive ? 'transform -rotate-45' : ''}`}></div>
            <div className={`bg-gray-500 rounded-full h-[2px] w-5 my-1 transition duration-300 ease-in-out ${isActive ? 'opacity-0' : ''}`}></div>
            <div className={`bg-gray-500 rounded-full h-[2px] w-5 my-1 transition duration-300 ease-in-out ${isActive ? 'transform rotate-45' : ''}`}></div>
        </div>
    );
};

const SmallBar = () => {
    return (
        <div className="w-20 border-r-[0.5px] border-gray-300 p-4">
            <div className="flex flex-col items-center justify-start">
                {/* <label className="w-10 h-10 rounded-full object-cover overflow-hidden bg-gray-100 border-1 border-gray-300 cursor-pointer">
                <input type="file" className="hidden" onChange={handleAvatarChange} />
                <img
                    src={avatar}
                    alt="Avatar"
                />
            </label> */}
                <MenuButton />
            </div>
        </div>
    )
}
export default SmallBar;