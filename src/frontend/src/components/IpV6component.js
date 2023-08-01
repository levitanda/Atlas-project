import React, { useState, useMemo, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Container, Row, Form, Button, Col } from "react-bootstrap";
import countryList from "react-select-country-list";

const DateTimeCountryForm = ({ updateData, initialData }) => {
  const handleSubmit = (event) => {
    event.preventDefault();
    const date1 = new Date(event.target.date1.value);
    const date2 = new Date(event.target.date2.value);
    const today = new Date();

    // set the hours, minutes, seconds and milliseconds to 0 to compare only the date part
    today.setHours(0, 0, 0, 0);
    date1.setHours(0, 0, 0, 0);
    date2.setHours(0, 0, 0, 0);

    if (date1 > today || date2 > today) {
      alert('Selected dates cannot be in the future!');
      return;
    }

    updateData({
      date1: event.target.date1.value,
      date2: event.target.date2.value,
      country: event.target.country.value,
    });
  };

  const country_options = useMemo(() => countryList().getData(), []);
  return (
    <Form onSubmit={handleSubmit}>
      <Container>
        <Row className="d-flex justify-content-center align-items-end">
          <Col md={3}>
            <Form.Group controlId="date1">
              <Form.Label>Reference Date</Form.Label>
              <Form.Control type="date" defaultValue={initialData["date1"]} />
            </Form.Group>
          </Col>
          <Col md={3}>
            <Form.Group controlId="date2">
              <Form.Label>Compare Date</Form.Label>
              <Form.Control type="date" defaultValue={initialData["date2"]} />
            </Form.Group>
          </Col>
          <Col md={3}>
            <Form.Group controlId="country">
              <Form.Label>Country</Form.Label>
              <Form.Select defaultValue={initialData["country"]}>
                {country_options.map((country) => (
                  <option key={country.value} value={country.value}>
                    {country.label}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
          <Col md={1} className="d-flex align-items-end justify-content-center" >
            <Button variant="primary" type="submit">
              Submit
            </Button>
          </Col>
        </Row>
      </Container>
    </Form>
  );
};

const AreaChartGraph = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" >
      <LineChart
        // width={1000}
        // height={450}
        data={data}
        margin={{
          top: 10,
          // right: 30,
          // left: 20,
          bottom: 10,
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
    </ResponsiveContainer>
  );
};

const AreaChart = () => {
  const [data, setData] = useState([]);

  const computeInitialData = () => {
    const get_current_date = () => new Date().toISOString().split("T")[0];
    const get_one_month_ago_from_today_date = () => {
      let date = new Date();
      date.setMonth(date.getMonth() - 1);
      return date.toISOString().split("T")[0];
    };
    return {
      date1: get_one_month_ago_from_today_date(),
      date2: get_current_date(),
      country: "IL",
    };
  };
  const [dates_country_data, updateData] = useState(computeInitialData());
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const country_code = dates_country_data["country"];
        const first_date = dates_country_data["date1"];
        const second_date = dates_country_data["date2"];
        setIsLoading(true);
        const response = await fetch(
          `/ipv/country=${country_code}&first_date=${first_date}&second_date=${second_date}`
        );
        const jsonData = await response.json();
        setData(jsonData.data);
        setIsLoading(false);
      } catch (error) {
        console.log(error.message);
      }
    };
    fetchData();
  }, [dates_country_data]);
  return (
    <Container>
      <Row className="justify-content-md=center">
        <Col md={12} style={{
                    marginTop: '10px',
                    height: '75vh',
                    border: '1px solid black',
                    borderRadius: '10px'
                }}>
          {!isLoading ? <AreaChartGraph data={data} /> : "Loading"}
        </Col>
      </Row>
      <Row>
        <Col md={12} >
          <DateTimeCountryForm
            updateData={updateData}
            initialData={computeInitialData()}
            
          />
        </Col>
      </Row>
    </Container>
  );
};

const IpV6component = () => {
  return <AreaChart />;
};

export default IpV6component;
