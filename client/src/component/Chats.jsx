"use client"
import React, { useState, useContext } from "react";
import ChatMessageGpt from "./ChatMessageGpt";
import ChatMessageUser from "./ChatMessageUser";
import { chatdetail } from "@/app/home/page";
import {ColorTheme} from "./ColorTheme";
import axios from "axios";


const Chats = () => {
  const { chatlog, setChatlog } = useContext(chatdetail);
  const [input, setInput] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    let newMessage = { user: "me", message: input };
    let chatLogNew=[...chatlog,newMessage];
    setChatlog(chatLogNew);

    setInput("");
    const chatmessage = newMessage.message;
    console.log("chatmessage", chatmessage);
    try {
      const response = await axios.get(`http://localhost:5000/api/chat?query=${chatmessage}`);
      console.log("Message sent successfully:", response);
      const gptMessage = { user: "gpt", message: response.data.response };
      setChatlog([...chatLogNew, gptMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  return (
    <>
      <div className="dark:bg-[#212121] bg-white w-full h-[100vh] flex flex-col overflow-y-scroll">
      <ColorTheme/>
        <div className="chat-log text-left">
          {chatlog.map(({ user, message, index }) => {
            if (user === "me") {
              return <ChatMessageUser message={message} />;
            } else if (user === "gpt") {
              return <ChatMessageGpt message={message} />;
            }
            return null;
          })}
        </div>
        <div>
          <div className="p-[30px] absolute bottom-0 left-[30rem]">
            <form onSubmit={handleSubmit}>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                rows="1"
                className="dark:bg-[#212121] bg-white border border-black dark:border-gray-500 w-[50rem] h-[3rem] rounded-lg outline-none text-black dark:text-white p-[10px]"
                placeholder="Message ChatGPT"
              ></input>
            </form>
          </div>
        </div>
      </div>
    </>
  );
};

export default Chats;
