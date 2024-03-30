"use client"
import React from "react";
// import { FaUserCircle } from "react-icons/fa";

const ChatMessageUser = ({ message }) => {
  return (
    <div>
      <div className="chat-message p-[12px] flex px-[40px] text-white ml-[10rem]">
      <div className="mb-[0.5rem] mt-[0.5rem] w-[40px] h-[40px] flex justify-center rounded-full bg-black text-white">
          <FaUserCircle className="w-[40px] h-[40px]" />
        </div>
        <div className="message px-[40px]">{message}</div>
      </div>
    </div>
  );
};

export default ChatMessageUser;
