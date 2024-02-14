import React from 'react'
import { Link } from 'react-router-dom'

const NavBar = () => {
  return (
    <nav className="d-flex justify-content-between">
      <img src="/assets/american_red_cross_logo.jpeg" alt="Logo" width="50" height="50" className="" />
      <ul className="d-flex list-unstyled gap-5">
        <li className="nav-item">
          <Link className="nav-link text-white fs-3 fw-medium" to={"/"}>Home</Link>
        </li>
        <li className="nav-item">
          <Link className="nav-link text-white fs-3 fw-medium" to={"/send-alert"}>Send Alert</Link>
        </li>
      </ul>

    </nav>
  );
}

export default NavBar