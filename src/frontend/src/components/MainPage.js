import { useState } from "react";
import Tab from "react-bootstrap/Tab";
import Tabs from "react-bootstrap/Tabs";
import DnsGraphComponent from "./DnsGraph";
import IpV6component from "./IpV6component";

function ControlledTabsExample() {
  const [key, setKey] = useState("DNS");

  return (
    <Tabs
      id="controlled-tab-example"
      activeKey={key}
      onSelect={(k) => setKey(k)}
      // className="mb-3"
    >
      <Tab eventKey="DNS" title="DNS availability">
        <DnsGraphComponent />
      </Tab>
      <Tab eventKey="IPv6" title="IPv6 deployment">
        <IpV6component />
      </Tab>
    </Tabs>
  );
}

export default ControlledTabsExample;
