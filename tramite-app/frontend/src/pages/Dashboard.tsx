import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Table, Form, Badge, Spinner, Card, Modal, Row, Col } from 'react-bootstrap';
import { Container } from 'react-bootstrap';
import { FiFileText, FiCheckCircle, FiClipboard, FiUserCheck, FiLogOut, FiEye, FiDownload } from 'react-icons/fi';

interface Tramite {
  id: number;
  tipo: string;
  fecha: string;
  nombreCliente: string;
  email: string;
  telefonoMovil: string;
  cups: string;
  direccion: string;
  refCatastral: string;
  potenciaNumerica: string;
  estado: string;
  dniPdf?: string;
  formatoAutorizacion?: string;
  plantillaRelacionPuntos?: string;
  // Campos específicos según el tipo
  aumentoPotencia?: boolean;
  vivienda?: string;
  variosSuministros?: boolean;
  acometidaCentralizada?: boolean;
}

const Dashboard = () => {
  const [userName, setUserName] = useState('');
  const [tramites, setTramites] = useState<Tramite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedTramite, setSelectedTramite] = useState<Tramite | null>(null);
  const navigate = useNavigate();

  // Efecto para registrar información del trámite seleccionado
  useEffect(() => {
    if (selectedTramite) {
      console.log('Documentos del trámite seleccionado:', {
        id: selectedTramite.id,
        dniPdf: selectedTramite.dniPdf,
        formatoAutorizacion: selectedTramite.formatoAutorizacion,
        plantillaRelacionPuntos: selectedTramite.plantillaRelacionPuntos
      });
    }
  }, [selectedTramite]);

  useEffect(() => {
    // Verificar si hay un token (usuario autenticado)
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    // Obtener datos del usuario desde el backend
    const fetchUserData = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/user', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setUserName(data.name);
        } else {
          // Si hay error de autenticación, redirigir a login
          localStorage.removeItem('token');
          navigate('/login');
        }
      } catch (error) {
        console.error('Error al obtener datos del usuario:', error);
      }
    };

    // Obtener los trámites desde el backend
    const fetchTramites = async () => {
      setLoading(true);
      try {
        const response = await fetch('http://localhost:5000/api/tramites', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log('Trámites recibidos del backend:', data);
          setTramites(data);
        } else {
          setError('Error al cargar los trámites. Por favor, inténtelo de nuevo.');
        }
      } catch (error) {
        console.error('Error al obtener trámites:', error);
        setError('Error de conexión con el servidor');
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
    fetchTramites();
  }, [navigate]);

  const handleEstadoChange = async (id: number, nuevoEstado: string) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch(`http://localhost:5000/api/tramites/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ estado: nuevoEstado })
      });

      if (response.ok) {
        // Actualizar el estado en la interfaz
        setTramites(tramites.map(tramite => 
          tramite.id === id ? {...tramite, estado: nuevoEstado} : tramite
        ));
      } else {
        setError('Error al actualizar el estado. Por favor, inténtelo de nuevo.');
      }
    } catch (error) {
      console.error('Error al actualizar estado:', error);
      setError('Error de conexión con el servidor');
    }
  };

  const getTipoIcon = (tipo: string) => {
    switch (tipo) {
      case 'Modificación':
        return <FiClipboard className="me-2" />;
      case 'Individual':
        return <FiFileText className="me-2" />;
      case 'Alta':
        return <FiCheckCircle className="me-2" />;
      default:
        return <FiFileText className="me-2" />;
    }
  };

  const openTramiteDetails = (tramite: Tramite) => {
    setSelectedTramite(tramite);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedTramite(null);
  };

  const handleViewPdf = (pdfName: string) => {
    if (!pdfName) return;
    
    // Obtener el token de autenticación
    const token = localStorage.getItem('token');
    if (!token) {
      setError('No está autenticado. Por favor, inicie sesión.');
      navigate('/login');
      return;
    }

    // Abrir el PDF en una nueva pestaña
    window.open(`http://localhost:5000/api/documents/${pdfName}?token=${token}`, '_blank');
  };

  const handleDownloadPdf = (pdfName: string) => {
    if (!pdfName) return;
    
    // Obtener el token de autenticación
    const token = localStorage.getItem('token');
    if (!token) {
      setError('No está autenticado. Por favor, inicie sesión.');
      navigate('/login');
      return;
    }

    // Iniciar la descarga del PDF
    window.location.href = `http://localhost:5000/api/documents/download/${pdfName}?token=${token}`;
  };

  return (
    <div className="fade-in-animation">
      <div className="dashboard-header">
        <Container>
          <Row className="align-items-center">
            <Col md={6}>
              <h2 className="mb-0 d-flex align-items-center">
                <FiFileText size={28} className="me-2" />
                Sistema de Trámites
              </h2>
            </Col>
            <Col md={6}>
              <div className="d-flex justify-content-md-end align-items-center gap-3">
                <div className="d-flex align-items-center">
                  <FiUserCheck size={20} className="me-2" />
                  <span>Bienvenido, <strong>{userName}</strong></span>
                </div>
                <Button 
                  variant="light" 
                  size="sm"
                  className="d-flex align-items-center" 
                  onClick={() => {
                    localStorage.removeItem('token');
                    navigate('/login');
                  }}
                >
                  <FiLogOut className="me-2" /> Cerrar Sesión
                </Button>
              </div>
            </Col>
          </Row>
        </Container>
      </div>

      <Container className="py-4">
        <Row className="mb-4">
          <Col xs={12} className="d-flex justify-content-end">
            <Button 
              variant="primary" 
              onClick={() => navigate('/formulario')}
              className="d-flex align-items-center"
            >
              <FiFileText className="me-2" /> Solicitud Expediente
            </Button>
          </Col>
        </Row>

        {error && (
          <Row className="mb-4">
            <Col>
              <div className="alert alert-danger">{error}</div>
            </Col>
          </Row>
        )}

        <Row>
          <Col>
            <Card>
              <Card.Header className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Trámites Registrados</h5>
                <Badge bg="primary" pill>
                  {tramites.length} {tramites.length === 1 ? 'registro' : 'registros'}
                </Badge>
              </Card.Header>
              <Card.Body>
                {loading ? (
                  <div className="text-center p-5">
                    <Spinner animation="border" role="status">
                      <span className="visually-hidden">Cargando...</span>
                    </Spinner>
                    <p className="mt-3 text-muted">Cargando trámites...</p>
                  </div>
                ) : tramites.length === 0 ? (
                  <div className="alert alert-info">
                    <p className="mb-0">No hay trámites registrados. Use el botón "Solicitud Expediente" para crear uno nuevo.</p>
                  </div>
                ) : (
                  <div className="table-responsive">
                    <Table striped hover className="mb-0">
                      <thead>
                        <tr>
                          <th>#</th>
                          <th>Tipo</th>
                          <th>Fecha</th>
                          <th>Cliente</th>
                          <th>CUPS</th>
                          <th>Estado</th>
                          <th>Acciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {tramites.map((tramite) => (
                          <tr key={tramite.id}>
                            <td>{tramite.id}</td>
                            <td>
                              <div className="d-flex align-items-center">
                                {getTipoIcon(tramite.tipo)}
                                {tramite.tipo}
                              </div>
                            </td>
                            <td>{tramite.fecha}</td>
                            <td>{tramite.nombreCliente}</td>
                            <td>
                              <span className="text-monospace small">{tramite.cups}</span>
                            </td>
                            <td>
                              <Badge 
                                bg={tramite.estado === 'Pendiente' ? 'warning' : 'success'}
                                className="px-3 py-2"
                              >
                                {tramite.estado}
                              </Badge>
                            </td>
                            <td>
                              <div className="d-flex align-items-center gap-2">
                                <Form.Select 
                                  size="sm" 
                                  value={tramite.estado}
                                  onChange={(e) => handleEstadoChange(tramite.id, e.target.value)}
                                  className="form-select-sm w-auto me-2"
                                >
                                  <option value="Pendiente">Pendiente</option>
                                  <option value="Completado">Completado</option>
                                </Form.Select>
                                <Button 
                                  variant="outline-info" 
                                  size="sm" 
                                  className="d-flex align-items-center"
                                  onClick={() => openTramiteDetails(tramite)}
                                >
                                  <FiEye className="me-1" /> Ver
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

      {/* Modal para ver detalles del trámite */}
      <Modal 
        show={showModal} 
        onHide={handleCloseModal} 
        size="lg" 
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>
            {selectedTramite && (
              <div className="d-flex align-items-center">
                {getTipoIcon(selectedTramite.tipo)}
                Trámite {selectedTramite.id} - {selectedTramite.tipo}
              </div>
            )}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedTramite && (
            <div>
              <div className="mb-4">
                <Badge 
                  bg={selectedTramite.estado === 'Pendiente' ? 'warning' : 'success'}
                  className="px-3 py-2 mb-3"
                >
                  {selectedTramite.estado}
                </Badge>
                <h5 className="mb-3">Información General</h5>
                <Row>
                  <Col md={6}>
                    <p><strong>Cliente:</strong> {selectedTramite.nombreCliente}</p>
                    <p><strong>Email:</strong> {selectedTramite.email}</p>
                    <p><strong>Teléfono:</strong> {selectedTramite.telefonoMovil}</p>
                    <p><strong>CUPS:</strong> {selectedTramite.cups}</p>
                  </Col>
                  <Col md={6}>
                    <p><strong>Dirección:</strong> {selectedTramite.direccion}</p>
                    <p><strong>Ref. Catastral:</strong> {selectedTramite.refCatastral}</p>
                    <p><strong>Potencia:</strong> {selectedTramite.potenciaNumerica}</p>
                    <p><strong>Fecha:</strong> {selectedTramite.fecha}</p>
                  </Col>
                </Row>
              </div>

              {/* Información específica según tipo de trámite */}
              {selectedTramite.tipo === 'Modificación' && (
                <div className="mb-4">
                  <h5 className="mb-3">Detalles de Modificación</h5>
                  <p><strong>Aumento de Potencia:</strong> {selectedTramite.aumentoPotencia ? 'Sí' : 'No'}</p>
                </div>
              )}

              {selectedTramite.tipo === 'Individual' && (
                <div className="mb-4">
                  <h5 className="mb-3">Detalles de Solicitud Individual</h5>
                  <p><strong>Vivienda:</strong> {selectedTramite.vivienda}</p>
                </div>
              )}

              {selectedTramite.tipo === 'Alta' && (
                <div className="mb-4">
                  <h5 className="mb-3">Detalles de Alta</h5>
                  <p><strong>Varios Suministros:</strong> {selectedTramite.variosSuministros ? 'Sí' : 'No'}</p>
                  <p><strong>Acometida Centralizada:</strong> {selectedTramite.acometidaCentralizada ? 'Sí' : 'No'}</p>
                </div>
              )}

              {/* Documentos */}
              <div>
                <h5 className="mb-3">Documentos</h5>
                <div className="d-flex flex-column gap-2">
                  
                  {selectedTramite.dniPdf && (
                    <Card className="bg-light">
                      <Card.Body className="d-flex justify-content-between align-items-center py-2">
                        <div className="d-flex align-items-center">
                          <FiFileText className="me-2" />
                          <span>DNI</span>
                        </div>
                        <div>
                          <Button 
                            variant="outline-primary" 
                            size="sm" 
                            className="me-2"
                            onClick={() => handleViewPdf(selectedTramite.dniPdf!)}
                          >
                            <FiEye className="me-1" /> Ver
                          </Button>
                          <Button 
                            variant="outline-success" 
                            size="sm"
                            onClick={() => handleDownloadPdf(selectedTramite.dniPdf!)}
                          >
                            <FiDownload className="me-1" /> Descargar
                          </Button>
                        </div>
                      </Card.Body>
                    </Card>
                  )}

                  {selectedTramite.formatoAutorizacion && (
                    <Card className="bg-light">
                      <Card.Body className="d-flex justify-content-between align-items-center py-2">
                        <div className="d-flex align-items-center">
                          <FiFileText className="me-2" />
                          <span>Formato de Autorización</span>
                        </div>
                        <div>
                          <Button 
                            variant="outline-primary" 
                            size="sm" 
                            className="me-2"
                            onClick={() => handleViewPdf(selectedTramite.formatoAutorizacion!)}
                          >
                            <FiEye className="me-1" /> Ver
                          </Button>
                          <Button 
                            variant="outline-success" 
                            size="sm"
                            onClick={() => handleDownloadPdf(selectedTramite.formatoAutorizacion!)}
                          >
                            <FiDownload className="me-1" /> Descargar
                          </Button>
                        </div>
                      </Card.Body>
                    </Card>
                  )}

                  {selectedTramite.plantillaRelacionPuntos && (
                    <Card className="bg-light">
                      <Card.Body className="d-flex justify-content-between align-items-center py-2">
                        <div className="d-flex align-items-center">
                          <FiFileText className="me-2" />
                          <span>Plantilla Relación Puntos</span>
                        </div>
                        <div>
                          <Button 
                            variant="outline-primary" 
                            size="sm" 
                            className="me-2"
                            onClick={() => handleViewPdf(selectedTramite.plantillaRelacionPuntos!)}
                          >
                            <FiEye className="me-1" /> Ver
                          </Button>
                          <Button 
                            variant="outline-success" 
                            size="sm"
                            onClick={() => handleDownloadPdf(selectedTramite.plantillaRelacionPuntos!)}
                          >
                            <FiDownload className="me-1" /> Descargar
                          </Button>
                        </div>
                      </Card.Body>
                    </Card>
                  )}

                  {!selectedTramite.dniPdf && !selectedTramite.formatoAutorizacion && !selectedTramite.plantillaRelacionPuntos && (
                    <p className="text-muted">No hay documentos disponibles para este trámite.</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseModal}>
            Cerrar
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default Dashboard; 