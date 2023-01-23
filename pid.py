class PID_CLASS():
    def __init__(self) -> None: 
        self.referencia: float = 0.0
        self.Kp: float = 0.0
        self.Ki: float = 0.0
        self.Kd: float = 0.0
        self.T: int = 1
        self.erro_total: float = 0.0
        self.erro_anterior: float = 0.0
        self.sinal_de_controle_MAX: float = 100.0
        self.sinal_de_controle_MIN: float = -100.0

    def configura_constantes(self, Kp: float, Ki: float, Kd: float) -> None:
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

    def atualiza_referencia(self, referencia: float) -> None:
        self.referencia = referencia

    def controle(self, saida_medida:float) -> float:
        erro: float = self.referencia - saida_medida

        self.erro_total += erro

        self.erro_total = min(self.erro_total, self.sinal_de_controle_MAX)
        self.erro_total = max(self.erro_total, self.sinal_de_controle_MIN)

        delta_error: float = erro - self.erro_anterior

        sinal_de_controle: float = self.Kp*erro + (self.Ki*self.T)*self.erro_total + (self.Kd/self.T)*delta_error

        sinal_de_controle = min(sinal_de_controle, self.sinal_de_controle_MAX)
        sinal_de_controle = max(sinal_de_controle, self.sinal_de_controle_MIN)

        self.erro_anterior = erro

        return sinal_de_controle
