import React, { useState } from 'react';
import { usStates, languageOptions, countiesByState } from '../data/state_county_data.js';
import axios from 'axios';
import { api_url } from '../data/api_endpoint.js';

function NewSubscriberForm() {

  const [formState, setFormState] = useState({
    fullName: '',
    email: '',
    phone: '',
    preferredLanguage: '',
    state: '',
    county: '',
  });

  const handleStateChange = (event) => {
    const selectedState = event.target.value;
    setFormState((prevFormState) => ({
      ...prevFormState,
      state: selectedState,
      county: '', // Reset county when state changes
    }));
  };

  const handleCountyChange = (event) => {
    const selectedCounty = event.target.value;
    setFormState((prevFormState) => ({
      ...prevFormState,
      county: selectedCounty,
    }));
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormState((prevFormState) => ({
      ...prevFormState,
      [name]: value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    axios.post(`${api_url}/subscribe`, formState, {
      headers: {
        'Content-Type': 'application/json',
      }})
      .then((response) => {
        console.log("successfully submitted and got back a response", response);
      })
      .catch((error) => {
        console.log("error submitting form", error);
      });
  };

  return (
    <>
    <h1 className='text-center mb-5'>Sign up for emergency alerts in your area</h1>
    <div className="d-flex gap-5">
      <div className="col-6 d-flex flex-column justify-content-center align-items-center">
        <img className="img-fluid" src="/assets/natural_disaster.jpeg" alt="natural disaster" />
      </div>
      <div className="col">
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="fullName" className="form-label">Full Name</label>
            <input type="text" className="form-control" id="fullName" name="fullName" placeholder='Full Name' value={formState.fullName} onChange={handleInputChange} />
          </div>

          <div className="mb-3">
            <label htmlFor="email" className="form-label">Email</label>
            <input type="email" className="form-control" id="email" name="email" placeholder="user@domain.com" value={formState.email} onChange={handleInputChange} />
          </div>

          <div className="mb-3">
            <label htmlFor="phone" className="form-label">Phone</label>
            <input type="tel" className="form-control" id="phone" name="phone" placeholder='1234657890' value={formState.phone} onChange={handleInputChange} />
          </div>

          <div className="mb-3">
            <label htmlFor="preferredLanguage" className="form-label">Preferred language</label>
            <select className="form-select" id="preferredLanguage" name="preferredLanguage" value={formState.preferredLanguage} onChange={handleInputChange}>
              <option defaultValue>Select preferred language</option>
              {languageOptions.map((language) => (
                <option key={language.value} value={language.value}>
                  {language.label}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-3">
            <label htmlFor="state" className="form-label">State</label>
            <select className="form-select" id="state" name="state" value={formState.state} onChange={handleStateChange}>
              <option defaultValue value="" disabled>Select State</option>
              {usStates.map((state, index) => (
                <option key={index} value={state}>
                  {state}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-3">
            <label htmlFor="county" className="form-label">County</label>
            <select className="form-select" id="county" name="county" onChange={handleCountyChange} defaultValue={"default"}>
              {formState.state === "" && <option value="default" disabled>Select County</option>}
              {formState.state && countiesByState[formState.state].map((county, index) => (
                <option key={index} value={county}>
                  {county}
                </option>
              ))}
            </select>
          </div>

          <button type="submit" className="btn btn-primary">Submit</button>
        </form>
      </div>
    </div>
    </>
  );
}

export default NewSubscriberForm;