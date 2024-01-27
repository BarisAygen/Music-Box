import React, { useState } from "react";
import axios from "axios";

export const Register = (props) => {
  const [name, setName] = useState("");
  const [surname, setSurname] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [pass, setPass] = useState("");


  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
        const response = await axios.post("http://localhost:5000/signup", {
            name: name,
            email: email,
            pass: pass
        });

        if (response.status === 201) {
            props.onFormSwitch('login');
        }
    } 
    catch (error) {
      console.log(error);
      alert("Email is already in use!");
    }
}

  return (
    <>
      <div className="auth-form-container">
        <form className="register-form" onSubmit={handleSubmit}>
          <h2>Register</h2>
          <label htmlFor="name">Name</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            name="name"
            id="Name"
            placeholder="Peace"
            required
            maxLength={50}
          />
          <label htmlFor="surname">Surname</label>
          <input
            value={surname}
            onChange={(e) => setSurname(e.target.value)}
            name="surname"
            id="surname"
            placeholder="Blackwater"
            required
            maxLength={50}
          />
          <label htmlFor="username">Username</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            name="username"
            id="username"
            placeholder="Peace_13"
            required
            maxLength={50}
          />
          <label htmlFor="email">Email</label>
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            placeholder="ilkan@gmail.com"
            name="email"
            id="email"
            required
            maxLength={50}
          />
          <label htmlFor="pass">Password</label>
          <input
            value={pass}
            onChange={(e) => setPass(e.target.value)}
            type="password"
            name="password"
            id="password"
            required
            maxLength={50}
          />
          <button type="submit">SIGN-UP</button>
        </form>
        <button className="link-btn" onClick={() => props.onFormSwitch("login")}>Already have an account?</button>
      </div>
    </>
  );
};
