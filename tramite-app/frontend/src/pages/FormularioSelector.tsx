import { useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';

const FormularioSelector = () => {
  const navigate = useNavigate();

  return (
    <Container className="py-5">
      <Row className="mb-4">
        <Col>
          <h2 className="text-center">Seleccione el tipo de trámite a realizar</h2>
        </Col>
      </Row>
      <Row>
        <Col md={4} className="mb-4">
          <Card className="h-100">
            <Card.Header className="bg-primary text-white">
              <h5 className="mb-0">Modificaciones en suministro existente</h5>
            </Card.Header>
            <Card.Body>
              <p>Para modificar uno o varios suministros o instalaciones existentes.</p>
              <ul>
                <li>Aumento de potencia</li>
                <li>Cambios en la instalación</li>
                <li>Modificaciones técnicas</li>
              </ul>
            </Card.Body>
            <Card.Footer>
              <Button 
                variant="primary" 
                className="w-100"
                onClick={() => navigate('/formulario/modificacion')}
              >
                Seleccionar
              </Button>
            </Card.Footer>
          </Card>
        </Col>
        
        <Col md={4} className="mb-4">
          <Card className="h-100">
            <Card.Header className="bg-success text-white">
              <h5 className="mb-0">Suministro individual</h5>
            </Card.Header>
            <Card.Body>
              <p>Para gestionar trámites relacionados con un único suministro.</p>
              <ul>
                <li>Suministro de obras</li>
                <li>Suministro eventual</li>
                <li>Local comercial</li>
                <li>Otros</li>
              </ul>
            </Card.Body>
            <Card.Footer>
              <Button 
                variant="success" 
                className="w-100"
                onClick={() => navigate('/formulario/individual')}
              >
                Seleccionar
              </Button>
            </Card.Footer>
          </Card>
        </Col>
        
        <Col md={4} className="mb-4">
          <Card className="h-100">
            <Card.Header className="bg-info text-white">
              <h5 className="mb-0">Alta de Nuevo Suministro</h5>
            </Card.Header>
            <Card.Body>
              <p>Para solicitar el alta de nuevos suministros eléctricos.</p>
              <ul>
                <li>Viviendas nuevas</li>
                <li>Locales comerciales</li>
                <li>Suministros múltiples</li>
              </ul>
            </Card.Body>
            <Card.Footer>
              <Button 
                variant="info" 
                className="w-100 text-white"
                onClick={() => navigate('/formulario/alta')}
              >
                Seleccionar
              </Button>
            </Card.Footer>
          </Card>
        </Col>
      </Row>
      
      <Row className="mt-4">
        <Col className="text-center">
          <Button 
            variant="outline-secondary" 
            onClick={() => navigate('/dashboard')}
          >
            Volver al Dashboard
          </Button>
        </Col>
      </Row>
    </Container>
  );
};

export default FormularioSelector; 