import React, {useState} from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Container, Row, Form, Button, Col, ButtonGroup } from 'react-bootstrap';
//import { CountryDropdown, RegionDropdown, CountryRegionData } from 'react-country-region-selector';
//import { getCountries } from 'react-intl-countries';
//import { countries } from 'countries-list';

const DateTimeForm = ({ updateDatesFunction, chosenDates }) => {
  const handleSubmit = (event) => {
      event.preventDefault();
      updateDatesFunction({ "date1": event.target.date1.value, "date2": event.target.date2.value });
  };
 /* const countries = getCountries('en'); // Get the list of countries in English
  const countryOptions = Object.entries(countries).map(([code, name]) => ({
    value: code,
    label: name,
  }));*/
  
  /*const countryOptions = Object.entries(countries).map(([code, name]) => ({
    value: code,
    label: name,
  }));*/
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
                  <Form.Control as="select">
                    {countryOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Control>
                </Form.Group>
              </Col>
          </Row>
          <Row>
              <Col></Col>
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
  const data = [
    {
      "name": "01/05/2023",
      "ipv6": 33.5,
      //"amt": 2400
    },
    {
      "name": "02/05/2023",
      "ipv6": 33.5,
      //"amt": 2210
    },
    {
      "name": "03/05/2023",
      "ipv6": 33.8,
      //"amt": 2290
    },
    {
      "name": "04/05/2023",
      "ipv6": 35,
      //"amt": 2000
    },
    {
      "name": "05/05/2023",
      "ipv6": 35.5,
      //"amt": 2181
    },
    {
      "name": "06/05/2023",
      "ipv6": 36,
      //"amt": 2500
    },
    {
      "name": "07/05/2023",
      "ipv6": 37,
      //"amt": 2100
    }
  ]
  const get_current_date = () => new Date().toISOString().split("T")[0]
  const [dates, setDates] = useState({ "date1": get_current_date(), "date2": get_current_date() });
  const [isLoading, setIsLoading] = useState(true);
  const [choosenResult, setSelectedButton] = useState("result1");
  const handleButtonClick = (button) => {
    setSelectedButton(button);
  };
  return (
      <Container id="chart" >
        <Row>
          <LineChart style={{
              width: '100%',
              height: '60vh',
              border: '1px solid black',
              borderRadius: '10px'
            }} 
            width={500}
            height={300}
            data={data}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name"  />
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
        </Row>
        <Row className="mb-3">
                <Col>
                    <DateTimeForm updateDatesFunction={setDates} chosenDates={dates} />
                </Col>
            </Row>
            {!isLoading ? (<Row >
                <Col>
                    <ButtonGroup>
                        <Button
                            variant={choosenResult === 'result1' ? 'primary' : 'secondary'}
                            onClick={() => handleButtonClick('result1')}
                        >
                            Show Result of First Date
                        </Button>
                        <Button
                            variant={choosenResult === 'result2' ? 'primary' : 'secondary'}
                            onClick={() => handleButtonClick('result2')}
                        >
                            Show Result of Second Date
                        </Button>
                    </ButtonGroup>
                </Col>
            </Row>) : ""}
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