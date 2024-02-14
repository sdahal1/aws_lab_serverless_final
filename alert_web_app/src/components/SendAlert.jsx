import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { usStates} from '../data/state_county_data.js';
import { api_url } from '../data/api_endpoint.js'


const SendAlert = () => {
  const [formState, setFormState] = useState({
    message: '',
    state: '',
  });

  const changeHandler = (event) => {
    setFormState((prevFormState) => ({
      ...prevFormState,
      [event.target.name]: event.target.value,
    }));
  }
  const handleSubmit = (event) => {
    event.preventDefault();
    axios.post(`${api_url}/sendAlert`, formState, {
      headers: {
        'Content-Type': 'application/json',
      }})
      .then((response) => {
        console.log("successfully submitted and got back a response", response);
      })
      .catch((error) => {
        console.log("error submitting form", error);
      });
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <h1 className='text-center mb-5'>Send an emergency alert</h1>
        <div className="mb-3">
          <label htmlFor="message" className="form-label">Alert Message</label>
          <textarea className="form-control" id="message" name="message" value={formState.message} onChange={changeHandler} />
        </div>

        <div className="mb-3">
          <label htmlFor="state" className="form-label">State</label>
          <select className="form-select" id="state" name="state" value={formState.state} onChange={changeHandler}>
            <option defaultValue value="" disabled>Select State</option>
            {usStates.map((state, index) => (
              <option key={index} value={state}>
                {state}
              </option>
            ))}
          </select>
        </div>

        <button type="submit" className="btn btn-primary">Submit</button>
      </form>
    </div>
  )
}

export default SendAlert