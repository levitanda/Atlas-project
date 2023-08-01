import React, { useState, useMemo, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Container, Row, Form, Button, Col, ButtonGroup } from 'react-bootstrap';
import Select from 'react-select'
import countryList from 'react-select-country-list'
import axios from 'axios';


function CountrySelector({ onChange }) {
  // change function signature , it need to accept update handler of parent
  const [value, setValue] = useState('')
  const options = useMemo(() => countryList().getData(), [])

  const changeHandler = value => {
    setValue(value)
    onChange(value)
    //call passed handler with value
  }
  return <Select options={options} value={value} onChange={changeHandler} />
}
const DateTimeForm = ({ updateDatesFunction, chosenDates, updateSelectedCountry, choosenCountry }) => {
  const handleSubmit = event => {
    event.preventDefault();
    updateDatesFunction({ "date1": event.target.date1.value, "date2": event.target.date2.value });
    //How to use choosen country?
    //updateSelectedCountry(choosenCountry);
    //console.log(choosenCountry);
  };

  const handleCountryChange = (value) => {
    updateSelectedCountry(value);
  };
  //define new state variable using useState


  // useEffect and call for server
  //console.log(choosenCountry)
  return (
    <Form onSubmit={handleSubmit}>
      <Row className="align-items-end">
        <Col md={4}>
          <Form.Group controlId="date1">
            <Form.Label>Reference Date</Form.Label>
            <Form.Control type="date"
              defaultValue={chosenDates["date1"]}
            />
          </Form.Group>
        </Col>
        <Col md={4}>
          <Form.Group controlId="date2">
            <Form.Label>Compare Date</Form.Label>
            <Form.Control type="date" defaultValue={chosenDates["date2"]} />
          </Form.Group>
        </Col>
        <Col md={4}>
          <Form.Group controlId="country">
            <Form.Label>Country</Form.Label>
            <CountrySelector onChange={handleCountryChange} />
          </Form.Group>
        </Col>
      </Row>
      <Row>
        <Col md={4} className="d-flex align-items-end justify-content-center">
          <Button variant="primary" type="submit">
            Submit
          </Button>
        </Col>
      </Row>
    </Form>
  );
};

const AreaChart = () => {
  const [data, setData] = useState([
    {
      "name": "01/05/2023",
      "ipv6": 33.5,
    },
    {
      "name": "02/05/2023",
      "ipv6": 33.5,
    },
    {
      "name": "03/05/2023",
      "ipv6": 33.8,
    },
    {
      "name": "04/05/2023",
      "ipv6": 35,
    },
    {
      "name": "05/05/2023",
      "ipv6": 35.5,
    },
    {
      "name": "06/05/2023",
      "ipv6": 36,
    },
    {
      "name": "07/05/2023",
      "ipv6": 37,
    }
  ])
  const get_current_date = () => new Date().toISOString().split("T")[0]
  const [dates, setDates] = useState({ "date1": get_current_date(), "date2": get_current_date() });
  const [selectedCountry, setSelectedCountry] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const [choosenResult, setSelectedButton] = useState("result1");
  const handleButtonClick = (button) => {
    setSelectedButton(button);
  };

  console.log(dates)
  console.log(selectedCountry)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const country_code = selectedCountry.value.substring(0, 2)
        setIsLoading(true);
        console.log(country_code);
        const response = await fetch(`/ipv/country=${country_code}&first_date=${dates["date1"]}&second_date=${dates["date2"]}`);
        const jsonData = await response.json();
        setData(jsonData.data);
        console.log(jsonData);
        setIsLoading(false);
      } catch (error) {
        console.log(error.message)
      }
    };
    fetchData();
  }, [dates, selectedCountry])
  return (
    <Container id="chart" >
      <br></br>
      {!isLoading ? (<Row>
        <LineChart
          width={1000}
          height={450}
          data={data}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="ipv6"
            stroke="#8884d8"
            activeDot={{ r: 8 }}
          />
        </LineChart>
      </Row>) : "Loading"}
      <Row className="mb-3">
        <Col>
          <DateTimeForm updateDatesFunction={setDates} chosenDates={dates} updateSelectedCountry={setSelectedCountry} choosenCountry={selectedCountry} />
        </Col>
      </Row>
    </Container>
  );
}

const IpV6component = () => {
  console.log("hey")
  return (
    <div>
      <AreaChart />
    </div>
  )
}

export default IpV6component